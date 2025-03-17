import os
import pandas as pd
import tempfile
from loguru import logger
import streamlit as st

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class EDI944Converter:
    """Class to convert tabular EDI 944 data to EDI 944 code format using LangChain and OpenAI API."""
    
    def __init__(self, api_key, mode="standard"):
        """
        Initialize the converter with OpenAI API key.
        
        Args:
            api_key (str): The OpenAI API key
            mode (str): The conversion mode. Either "standard" or "synapse"
        """
        self.api_key = api_key
        self.mode = mode
        
        # Initialize LangChain components with ChatOpenAI for chat models
        self.llm = ChatOpenAI(temperature=0.1, api_key=api_key, model_name="gpt-4")
        
        # Define the prompt template for standard EDI 944 conversion
        self.standard_template = """
        You are an expert in EDI (Electronic Data Interchange) formats, specifically focused on the EDI 944 
        Warehouse Stock Transfer Receipt Advice format. Your task is to convert tabular data into proper 
        EDI 944 code format that exactly follows the client's expected output structure.
        
        IMPORTANT FORMAT REQUIREMENTS:
        1. Use asterisk (*) as element separator and tilde (~) as segment terminator
        2. Include ISA/GS/ST header segments exactly as shown in the example
        3. Use W17 segment (NOT W27) for warehouse receipt identification
        4. Include N1 segments for entity identification
        5. Include N9 segments for reference information
        6. Use W07 segments (NOT W12) for item details
        7. Include G69 segments for item descriptions
        8. Add reference N9 segments for item attributes (colors, dimensions, weights)
        9. End with W14 segment for totals
        10. Close with SE/GE/IEA segments
        
        EDI 944 SEGMENT STRUCTURE:
        - ISA segment: ISA*00          00          ZZ*[sender]            ZZ*[receiver]     [date]*[time]*U*00401*[control#]*1*P*>~
        - GS segment: GS*RE*[sender]*[receiver]*[date]*[time]*[control#]*X*004010~
        - ST segment: ST*944*0001~
        - W17 segment: W17*[type]*[date]*[receipt-ID]*[shipment-ID]*[container-ID]*[count]*[quantity]~
        - N1 segment: N1*[entity type]*[entity ID]~
        - N9 segment: N9*[reference qualifier]*[reference ID]~
        - W07 segment: W07*[quantity]*[unit]*[product ID]*[qualifier]*[product code]~
        - G69 segment: G69*[product description]~
        - W14 segment: W14*[total quantity]~
        - SE segment: SE*[segment count]*0001~
        - GE segment: GE*1*[control#]~
        - IEA segment: IEA*1*[control#]~
        
        Sample REFERENCE EXAMPLE:
        
        Input:
        HDR|CAN|944|O|753515|1|753515-1|BSIU9579971|20250303||||OCEA|24940|R|20172|20172|20172|0|3/4/2025 4:47:26 PM||MIDAS EXPRESS INC. (LYNWOOD)||||||||CAN||||CHILDREN'S APPAREL NETWORK|LYN|||||||||||||||||||||||||||0|LYN|||||||||||||||||||||||||JESSICAL|
        DTL|45|PBDCB81-MFA|NA||EA|2340|1.3542|2340|1.3542|0|2340|1|N|L|0.000783680555555556|CF||||||||||||||||||||||||||||||45|||||||0||||||0|3/4/2025 4:47:26 PM|||18|17|8|8
        DTL|46|PBDCB82-MFA|NA||EA|1188|0.6875|1188|0.6875|0|1188|1|N|L|0.000397858796296296|CF||||||||||||||||||||||||||||||46|||||||0||||||0|3/4/2025 4:47:26 PM|||18|17|8|8
        DTL|41|PBDM708-MFA|NA||EA|1800|1.0417|1800|1.0417|0|1800|1|N|L|0.000602835648148148|CF||||||||||||||||||||||||||||||41|||||||0||||||0|3/4/2025 4:47:26 PM|||16|14|8|5
        
        Sample EDI 944 code:
        ISA*00          00          ZZ*DCG            ZZ*9083514477     220519*0800*U*00401*000001057*1*P*>~GS*RE*DCG*9083514477*20220519*0800*1057*X*004010~ST*944*0001~W17*F*20220516*EISU9397985-21104*21104*EISU9397985*9*1337~N1*WH*D7~N9*ZZ*EISU9397985~N9*IN*0100-128E EGLV11020001328~W07*3024*EA*196272171026*VN*HCZK203-STK~G69*3PC LIFE WITH MAMMALS SHORT SET~N9*CL*GREY~N9*SZ*PPK~N9*PO*CS22/0406~N9*LN*18.000~N9*WD*13.000~N9*HT*19.000~N9*WT*24.200~W07*6000*EA*196272482689*VN*HCZK403-STK~G69*3PC LIFE WITH MAMMALS SHORT SET~N9*CL*GREY~N9*SZ*PPK~N9*PO*CS22/0406~N9*LN*18.000~N9*WD*13.000~N9*HT*19.000~N9*WT*27.940~W14*31248~SE*70*0001~GE*1*1057~IEA*1*000001057~
        
        
        
        HANDLING EDGE CASES:
        1. If minimal data is provided, create appropriate placeholder values
        2. Include appropriate reference segments even if not explicitly in input
        3. Always use the correct delimiters as specified (*) and (~)
        4. Always include the complete set of required segments
        
        Convert the following tabular EDI 944 data into proper EDI 944 code format:
        
        {tabular_data}
        
        Provide ONLY the resulting EDI 944 code with no additional explanations, comments, or markdown.
        """
        # Define the prompt template for Synapse-specific EDI 944 conversion
        self.synapse_template = """
Your task is to convert Synapse EDI 944 data (tabular data) into standard EDI 944 code.

Note that the following examples are not inter-related. These are just examples for reference.

Sample Synapse EDI 944 data (Tabular):
HDR|CAN|944|O|753515|1|753515-1|BSIU9579971|20250303||||OCEA|24940|R|20172|20172|20172|0|3/4/2025 4:47:26 PM||MIDAS EXPRESS INC. (LYNWOOD)||||||||CAN||||CHILDREN'S APPAREL NETWORK|LYN|||||||||||||||||||||||||||0|LYN|||||||||||||||||||||||||JESSICAL|
DTL|45|PBDCB81-MFA|NA||EA|2340|1.3542|2340|1.3542|0|2340|1|N|L|0.000783680555555556|CF||||||||||||||||||||||||||||||45|||||||0||||||0|3/4/2025 4:47:26 PM|||18|17|8|8
DTL|46|PBDCB82-MFA|NA||EA|1188|0.6875|1188|0.6875|0|1188|1|N|L|0.000397858796296296|CF||||||||||||||||||||||||||||||46|||||||0||||||0|3/4/2025 4:47:26 PM|||18|17|8|8
DTL|41|PBDM708-MFA|NA||EA|1800|1.0417|1800|1.0417|0|1800|1|N|L|0.000602835648148148|CF||||||||||||||||||||||||||||||41|||||||0||||||0|3/4/2025 4:47:26 PM|||16|14|8|5
DTL|42|PBDM709-MFA|NA||EA|1152|0.6667|1152|0.6667|0|1152|1|N|L|0.000385821759259259|CF||||||||||||||||||||||||||||||42|||||||0||||||0|3/4/2025 4:47:26 PM|||16|14|8|5
DTL|43|PBDM908-MFA|NA||EA|2352|1.3611|2352|1.3611|0|2352|1|N|L|0.000787673611111111|CF||||||||||||||||||||||||||||||43|||||||0||||||0|3/4/2025 4:47:26 PM|||17|15|8|7
DTL|44|PBDM909-MFA|NA||EA|1776|1.0278|1776|1.0278|0|1776|1|N|L|0.000594791666666667|CF||||||||||||||||||||||||||||||44|||||||0||||||0|3/4/2025 4:47:26 PM|||17|15|8|7
DTL|40|PBGGB06-TJH|NA||EA|3600|2.0833|3600|2.0833|0|3600|1|N|L|0.00120561342592593|CF||||||||||||||||||||||||||||||40|||||||0||||||0|3/4/2025 4:47:26 PM|||19|16|11|20
DTL|37|PDUS902-LIC|NA||EA|6|0.0035|6|0.0035|0|6|1|N|L|2.02546296296296E-6|CF||||||||||||||||||||||||||||||37|||||||0||||||0|3/4/2025 4:47:26 PM|||16|16|4|4
DTL|38|PDUS902-MAR|NA||EA|5952|3.4444|5952|3.4444|0|5952|1|N|L|0.00199328703703704|CF||||||||||||||||||||||||||||||38|||||||0||||||0|3/4/2025 4:47:26 PM|||32|17|17|30
DTL|39|PYMW902-LIC|NA||EA|6|0.0035|6|0.0035|0|6|1|N|L|2.02546296296296E-6|CF||||||||||||||||||||||||||||||39|||||||0||||||0|3/4/2025 4:47:26 PM|||16|14|6|4

Sample EDI 944 code:
ISA*00          00          ZZ*DCG            ZZ*9083514477     220519*0800*U*00401*000001057*1*P*>~GS*RE*DCG*9083514477*20220519*0800*1057*X*004010~ST*944*0001~W17*F*20220516*EISU9397985-21104*21104*EISU9397985*9*1337~N1*WH*D7~N9*ZZ*EISU9397985~N9*IN*0100-128E EGLV11020001328~W07*3024*EA*196272171026*VN*HCZK203-STK~G69*3PC LIFE WITH MAMMALS SHORT SET~N9*CL*GREY~N9*SZ*PPK~N9*PO*CS22/0406~N9*LN*18.000~N9*WD*13.000~N9*HT*19.000~N9*WT*24.200~W07*6000*EA*196272482689*VN*HCZK403-STK~G69*3PC LIFE WITH MAMMALS SHORT SET~N9*CL*GREY~N9*SZ*PPK~N9*PO*CS22/0406~N9*LN*18.000~N9*WD*13.000~N9*HT*19.000~N9*WT*27.940~W07*6000*EA*196272598878*VN*HCZK404-STK~G69*3PC TINY BUT MIGHTY SHORT SET~N9*CL*GREEN~N9*SZ*PPK~N9*PO*CS22/0406~N9*LN*20.000~N9*WD*14.500~N9*HT*19.500~N9*WT*27.500~W07*3024*EA*196272729241*VN*HCZK206-STK~G69*3PC LION SHORT SET~N9*CL*YELLO~N9*SZ*PPK~N9*PO*CS22/0407~N9*LN*18.000~N9*WD*13.000~N9*HT*19.000~N9*WT*45.760~W07*6000*EA*196272730063*VN*HCZK406-STK~G69*3PC LION SHORT SET~N9*CL*YELLO~N9*SZ*PPK~N9*PO*CS22/0407~N9*LN*20.000~N9*WD*14.000~N9*HT*19.000~N9*WT*27.060~W07*6000*EA*196272215515*VN*HCZK606-STK~G69*3PC LION SHORT SET~N9*CL*YELLO~N9*SZ*PPK~N9*PO*CS22/0407~N9*LN*22.000~N9*WD*14.000~N9*HT*19.000~N9*WT*32.520~W07*1200*EA*196272246359*VN*HCZW823-STK~G69*3PC BUG EXPERT SHORT SET~N9*CL*WHITE~N9*SZ*PPK~N9*PO*CS22/0408~N9*LN*22.000~N9*WD*16.000~N9*HT*24.000~N9*WT*36.520~W14*31248~SE*70*0001~GE*1*1057~IEA*1*000001057~


   HANDLING EDGE CASES:
   1. If minimal data is provided, create appropriate placeholder values
   2. Include appropriate reference segments even if not explicitly in input
   3. CRITICAL: ALWAYS use asterisk (*) as element separator and tilde (~) as segment terminator after EVERY segment
   4. Always include the complete set of required segments
   5. Use N1*WH for warehouse and N1*ST for store/supplier consistently
   6. Ensure date formats are YYYYMMDD in all segments
   
Convert the following Synapse EDI 944 data (tabular) to standard EDI 944 code format:

{tabular_data}

Provide ONLY the resulting standard EDI 944 code with no explanations, comments, or markdown.
"""
        
        # Select the appropriate template based on the mode
        template = self.standard_template if mode == "standard" else self.synapse_template
        
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["tabular_data"]
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        
    def convert_tabular_to_edi944(self, tabular_data):
        """
        Convert tabular EDI 944 data to EDI 944 code format.
        
        Args:
            tabular_data (str): The tabular data in string format
            
        Returns:
            str: The converted EDI 944 code
        """
        try:
            mode_str = "standard" if self.mode == "standard" else "Synapse-specific"
            logger.info(f"Starting conversion from tabular to {mode_str} EDI 944 format using LangChain")
            
            # Use LangChain to process the conversion
            result = self.chain.invoke({"tabular_data": tabular_data})
            
            # The result structure might be different based on LangChain version
            if isinstance(result, dict) and "text" in result:
                edi944_code = result["text"].strip()
            else:
                edi944_code = str(result).strip()
            
            logger.info(f"Successfully converted tabular data to {mode_str} EDI 944 format")
            return edi944_code
            
        except Exception as e:
            error_msg = f"Error during conversion: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
    def save_to_file(self, edi944_code):
        """
        Save the EDI 944 code to a temporary file.
        
        Args:
            edi944_code (str): The EDI 944 code to save
            
        Returns:
            str: Path to the saved file
        """
        try:
            mode_str = "standard" if self.mode == "standard" else "synapse"
            logger.info(f"Saving {mode_str} EDI 944 code to temporary file")
            
            # Create a temporary file
            fd, temp_path = tempfile.mkstemp(suffix='.txt', prefix=f'edi944_{mode_str}_')
            os.close(fd)
            
            # Write the EDI 944 code to the file
            with open(temp_path, 'w') as f:
                f.write(edi944_code)
                
            logger.info(f"EDI 944 code saved to {temp_path}")
            return temp_path
            
        except Exception as e:
            error_msg = f"Error saving EDI 944 code to file: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
