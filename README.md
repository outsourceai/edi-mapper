# EDI 944 Mapper

An AI-powered Streamlit application that converts tabular EDI 944 data to standard EDI 944 code format using LangChain.

## Features

- **Dual Conversion Support**:
  - Standard EDI 944 conversion (general EDI specifications)
  - Synapse-specific EDI 944 conversion (custom format for Synapse systems)
- User-friendly interface with separate tabs for each conversion type
- Secure OpenAI API key management (keys are stored only in session state)
- Download functionality for the generated EDI 944 code
- Conversion history tracking
- Comprehensive error handling and logging
- API key testing tool for troubleshooting

## Requirements

- Python 3.8 or higher
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd edi-mapper-v2
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application using the provided batch file:
```bash
./run_app.bat
```

2. Choose either the main application or the API test tool

3. Access the application in your web browser (usually at http://localhost:8501)

4. Enter your OpenAI API key in the sidebar (this is required for the application to work)

5. Select the appropriate conversion tab:
   - **Standard EDI 944**: For general EDI 944 conversion following standard formats
   - **Synapse EDI 944**: For Synapse-specific EDI 944 format conversion

6. Paste your tabular EDI 944 data into the text area

7. Click "Convert to Standard EDI 944" or "Convert to Synapse EDI 944" as appropriate

8. View the generated EDI 944 code and download it as needed

## Conversion Types

### Standard EDI 944 Conversion

The standard conversion follows general EDI 944 specifications with these key segments:
- ISA: Interchange Control Header
- GS: Functional Group Header
- ST: Transaction Set Header (944)
- W27: Warehouse Receipt Identification
- LX: Assigned Number
- W12: Warehouse Item Detail
- SE: Transaction Set Trailer
- GE: Functional Group Trailer
- IEA: Interchange Control Trailer

### Synapse EDI 944 Conversion

The Synapse conversion creates a custom format specifically designed for Synapse systems:
- HDR record with 89 fields, containing header information
- DTL records with 67 fields for each line item
- Follows the exact field specifications required by Synapse systems

## Troubleshooting API Key Issues

If you encounter issues with your OpenAI API key:

1. Use the API Test Tool option when starting the application (option 2 in the batch file)
2. Enter your API key and test the connection
3. Check for any specific error messages
4. Verify your API key is valid and has available credits
5. Make sure you have a working internet connection

## Application Structure

- `app.py`: Main entry point for the Streamlit application
- `run_app.bat`: Batch file to run either the main app or API test tool
- `test_api.py`: Standalone API key testing tool
- `direct_test.py`: Alternative API key testing tool
- `app/`
  - `main.py`: Core Streamlit application logic and UI
  - `config.py`: Configuration and session state management
  - `converter.py`: EDI 944 conversion logic for both standard and Synapse formats
- `logs/`: Directory where application logs are stored

## Technology Stack

This application uses:
- **LangChain** for OpenAI API integration
- **Streamlit** for the web interface
- **GPT-4** for intelligent conversion of tabular data to EDI 944 formats
- **Python** with modern libraries for robust application development

## Security Considerations

- OpenAI API keys are stored only in session state and not persisted to disk
- Each user needs to provide their own API key
- No sensitive data is stored permanently

## Development Notes

### EDI 944 Format

The EDI 944 (Warehouse Stock Transfer Receipt Advice) is a document that notifies a trading partner that a warehouse transfer receipt shipment has been received and verified (or rejected).

#### Standard EDI 944 Format
Key segments in a standard EDI 944 include:
- ISA: Interchange Control Header
- GS: Functional Group Header
- ST: Transaction Set Header
- W17: Warehouse Receipt Identification (client-specific requirement)
- N1: Entity Identification
- N9: Reference Information
- W07: Item Detail (client-specific requirement)
- G69: Item Description
- W14: Total field for item quantities
- SE: Transaction Set Trailer
- GE: Functional Group Trailer
- IEA: Interchange Control Trailer

**Note:** The client's specific implementation uses W17/W07 segments (not W27/W12 as in some standard implementations), and requires asterisk (*) element separators with tilde (~) segment terminators.

#### Synapse EDI 944 Format
The Synapse format is a custom implementation with these characteristics:
- Uses pipe (|) delimiters throughout
- Contains one HDR record with 89 fields
- Contains multiple DTL records with 67 fields each
- Follows a strict field structure that must be preserved exactly

### Client-Specific Requirements

Based on client sample data, the application implements these specific format requirements:
1. For Standard EDI 944:
   - Proper reference segments (N9) for item attributes
   - G69 segments for item descriptions
   - W17/W07 structure instead of W27/W12
   - Exact delimiter usage (asterisks/tildes)

2. For Synapse EDI 944:
   - Exact field count and position maintenance
   - Preservation of all empty fields
   - Specific status code handling

### Recent Enhancements

- Improved conversion templates with client-specific examples
- Better handling of reference segments and item attributes
- Enhanced status code translation
- Streamlined API validation process
- Added API testing tools for troubleshooting

## License

[MIT License](LICENSE)

## Acknowledgements

This application is built using:
- [Streamlit](https://streamlit.io/)
- [LangChain](https://www.langchain.com/)
- [OpenAI API](https://openai.com/api/)
- [Pandas](https://pandas.pydata.org/)
- [Loguru](https://github.com/Delgan/loguru) 