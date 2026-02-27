# Currency Converter with AWS S3 & Pandas Analytics

## 📋 Description
Advanced currency converter that integrates external API, AWS S3 cloud storage, and Pandas data analytics. The application allows real-time currency conversion, stores conversion history in the cloud, and generates detailed analytical reports.

## 🚀 Features

### 💱 Currency Conversion
- Real-time currency conversion using ExchangeRate API
- Support for multiple currencies (USD, EUR, GBP, PLN, etc.)
- Display of current exchange rates

### ☁️ AWS S3 Integration
- Automatic saving of each conversion to AWS S3
- Conversion history retrieval from cloud
- File management (search, delete, deduplicate)
- Conversion statistics

### 📊 Pandas Analytics
- Advanced data analysis with Pandas
- Conversion statistics (sum, average, min, max)
- Most popular currency pairs
- Daily conversion reports
- Top largest conversions

### 🛠️ Additional Features
- Find largest file in S3
- Calculate total size of all conversions
- Find newest conversion
- Remove duplicate conversions
- Clean all conversions (fresh start)

## 🔧 Technologies
- **Python 3.x**
- **boto3** - AWS SDK for Python
- **pandas** - Data analysis library
- **requests** - HTTP library for API calls
- **AWS S3** - Cloud storage

## 📦 Installation

1. Clone repository:
```bash
git clone https://github.com/YOUR_USERNAME/currency-converter-aws-pandas.git
cd currency-converter-aws-pandas
```

2. Install dependencies:
```bash
pip install boto3 pandas requests
```

3. Configure AWS credentials:
```bash
aws configure
```
Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `eu-central-1`)

4. Create S3 bucket or use existing one

## ⚙️ Configuration

Edit the main program section:
```python
if __name__ == "__main__":
    calc = CurrencyConverterFull(
        'YOUR_API_KEY',           # ExchangeRate API key
        'YOUR_BUCKET_NAME'        # AWS S3 bucket name
    )
    calc.run()
```

## 🎯 Usage

Run the program:
```bash
python currency_converter_full.py
```

### Menu Options:
1. **Convert currency** - Perform currency conversion
2. **Get conversions count** - Show number of saved conversions
3. **Display conversion history** - Show all conversions from S3
4. **Get conversion statistics** - Basic statistics
5. **Show Pandas report** - Advanced analytics with Pandas
6. **Find largest file** - Find largest conversion file
7. **Get total size** - Calculate total size of all conversions
8. **Find newest file** - Find most recent conversion
9. **Remove duplicates** - Delete duplicate conversions
10. **Delete all conversions** - Fresh start
0. **Exit** - Close program

## 📊 Example Pandas Report

```
📊 ADVANCED PANDAS REPORT
======================================================================

1️⃣ BASIC INFO:
   Total conversions: 25
   Date range: 2026-02-20 to 2026-02-27

2️⃣ TOP 5 CURRENCY PAIRS:
USD → EUR    10
GBP → PLN     8
EUR → USD     4

3️⃣ AMOUNT STATISTICS:
count    25.000000
mean    523.400000
std     312.156789
min     100.000000
max    1500.000000

4️⃣ TOTAL AMOUNT BY FROM_CURRENCY:
               sum        mean  count
from_currency                       
EUR          2500.50    625.13      4
GBP          4200.00    525.00      8
USD          6384.50    638.45     10
```

## 📁 Project Structure
```
currency-converter-aws-pandas/
│
├── currency_converter_full.py    # Main program file
├── README.md                      # Documentation
└── requirements.txt               # Dependencies
```

## 🔐 Security
- Never commit AWS credentials to repository
- Use environment variables or AWS IAM roles
- Keep API keys secure

## 📝 Requirements
```
boto3>=1.26.0
pandas>=2.0.0
requests>=2.28.0
```

## 🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first.

## 👩‍💻 Author
Jolanta - [GitHub Profile](https://github.com/jolanta-kowalewska)

## 📄 License
MIT

---
⭐ If you like this project, give it a star on GitHub!
