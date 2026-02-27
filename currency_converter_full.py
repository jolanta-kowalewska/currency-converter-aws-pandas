#currency_converter_full.py
import boto3
import json
from datetime import datetime
from collections import Counter, defaultdict
import statistics
import requests
import pandas as pd

"""Currency converter with API, AWS S3, Pandas"""
class CurrencyConverterFull:
    #API integration
    def __init__(self,api_key, bucket_name):
        self.api_key = api_key
        self.base_url = "https://api.exchangerate-api.com/v4/latest/"
        self.history = [] #a list to collect all currency conversions 

    #AWS integration
        self.s3 = boto3.client('s3')   #łacze sie z s3
        self.bucket = bucket_name     #nazwa dla bucket

        self.menu = {
            1:("Convert currency", self.convert_currency),
            2:("Get conversions count", self.get_conversion_count),
            3:("Display conversion history", self.display_history),
            4:("Get conversion statistics", self.get_conversion_stats),
            5:("Show Pandas report", self.pandas_report),
            6:("Find the largest file in conversions", self.find_largest_file),
            7:("Get the total size of all conversion", self.get_total_size),
            8:("Find the newest file", self.find_newest_file),
            9:("Remove duplicate conversions",self.remove_duplicate_conversions),
            10:("Delete all conversions (fresh start)",self.clean_old_conversions),
            0:("Exit", self.exit)
        }


    # ===== PART 1: API CONVERSION =====
    
    #get the currency rates from API
    def get_exchange_rate(self, from_currency, to_currency):
        #API call to get the current rates
        try:
            url = f"{self.base_url}{from_currency}"
            response = requests.get(url, timeout=5)
            data = response.json()
                  
            response.raise_for_status() #check if response 200
            
            if to_currency in data['rates']:
                return data['rates'][to_currency]  # here we get the rates!
            else:
                print(f"❌ Currency {to_currency} not found")
                return None

        except requests.exceptions.RequestException as e:
            print(f"API conection error: {e}")
            
        except KeyError:
            print("API response error")      

    #currency converter
    def convert_currency(self):
        
        #getting from_currency and to_currency
        from_currency = input("From currency: (example: USD): ").upper()
        to_currency = input("To currency: (example: EUR): ").upper()

        try:
            amount = float(input("Amount to convert: "))  
        except ValueError:
            print("Invalid! Please provide correct amount.")
            return   

        

        rate = self.get_exchange_rate(from_currency,to_currency)

        if rate:
            
            #conversion result
            result = float(amount) * float(rate)
            
            #text result           
            print(f"\n{amount} {from_currency} = {result:.2f} {to_currency}")           #:.2f for float 2 numbers after '.'
            print(f"📊Rate: {rate} {to_currency}")                              #:.4f for float 4 numbers after '.'


            #save to S3
            self.save_conversion_to_s3(from_currency,to_currency,amount,result,rate)

            return result
        return None
    
    # ===== PART 2: AWS S3 =====

    def save_conversion_to_s3(self, from_currency, to_currency, amount, result, rate):
        """Save conversion to S3"""
        conversion_data = {
            'from_currency': from_currency,
            'to_currency': to_currency,
            'amount': amount,
            'result': result,
            'rate': rate,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        filename = f"conversions/{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"

        self.s3.put_object(
            Bucket=self.bucket,
            Key=filename,
            Body=json.dumps(conversion_data, indent=2)
        )

        print(f"✅ Saved to S3: {filename}")
        return filename


    def get_all_conversions(self):
        """Get the conversion from S3"""

        try:
            print(f"Reading from bucket {self.bucket}")

            response = self.s3.list_objects_v2(
                Bucket = self.bucket,
                Prefix = 'conversions/'
            )

            #check files

            if 'Contents' not in response:
                print("⚠️ No files in conversions/ folder")
                return []
            
            print(f"Found {len(response['Contents'])} files")

            conversions = []
            for obj in response['Contents']:
                key = obj['Key']
                

                try:
                    #get the file
                    file_obj = self.s3.get_object(Bucket = self.bucket,Key = key)

                    #read the content of a file
                    content = file_obj['Body'].read().decode('utf-8')
                    data = json.loads(content)
                    conversions.append(data)
                    
                except Exception as e:
                    print(f"   ❌ Error reading {key}: {e}")
                    continue 

            print(f"✅ Successfully read {len(conversions)} conversions")
            return conversions
               
        except Exception as e:
            print(f"⚠️ Error: {e}")
            import traceback
            traceback.print.exc()
            return []


    def get_conversion_count(self):
        """How many conversions in S3"""
        try:
            response = self.s3.list_objects_v2(
                Bucket = self.bucket,
                Prefix = 'conversions/'
            )
            count = len(response.get('Contents',[]))
            print(f"Found {count} conversion files.")
            return count
        except Exception as e:
            print(f"❌ Error counting: {e}")
            return 0

    def display_history(self):
        """Display history conversion""" 
        print("\n"+"+" * 70)
        print(f"\n📊 CONVERSION HISTORY FROM AWS S3 ")
        print("=" * 70)

        conversions = self.get_all_conversions()

        if not conversions:
            print("\n📭 No conversions in S3 yet")
            return
        
        print(f"\n Found {len(conversions)} conversions:\n")

        for i, conv in enumerate(conversions, 1):
            print(f"{i}. {conv['from_currency']} -> {conv['to_currency']}")
            print(f"   Amount: {conv['amount']}")
            print(f"   Result: {conv['result']}")
            print(f"   Rate: {conv['rate']}")
            print(f"   Time: {conv['timestamp']}")
            print()

        print("=" * 70)    

    def clean_old_conversions(self):
        """Delete all old conversions (fresh start)"""
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix = 'conversions/'
            )

            if 'Contents' not in response:
                print("✅ No files to delete")
                return
        
            for obj in response['Contents']:
                self.s3.delete_object(
                    Bucket = self.bucket,
                    Key = obj["Key"]
                )
                print(f"🗑️Deleted: {obj['Key']}")

        except Exception as e:
            print(f"❌Error: {e}")
                
    def find_largest_file(self):
        """ Find the largest file in conversions"""
        try:
            response = self.s3.list_objects_v2(
            Bucket=self.bucket,
            Prefix = 'conversions/'
            )

            if 'Contents' not in response:
                print("✅ No files to check")
                return  None

            print(f"Found {len(response['Contents'])} files")

            #file list:
            files = response['Contents']
            #find the largest
            largest_file = max(files, key = lambda x: x['Size'])

            largest_file_name = largest_file['Key']
            print(f"The largest file is {largest_file_name}")
            return largest_file_name
        
        except Exception as e:
            print(f"❌Error: {e}")

    def get_total_size(self):
        """Get the total size of all conversions"""

        try:
            response = self.s3.list_objects_v2(
            Bucket=self.bucket,
            Prefix = 'conversions/'
            )

            if 'Contents' not in response:
                print("✅ No files to check")
                return  0

            print(f"Found {len(response['Contents'])} files")

            #file list:
            files = response['Contents']

            #sum of files:
            file_sum = sum(f['Size'] for f in files)
            # kb conversion 
            total_kb = file_sum / 1024
            print(f"The size sum of all files is: {total_kb} kb.")
            return total_kb  

        except Exception as e:
            print(f"❌Error: {e}")
   
    def find_newest_file(self):
        # find the latest file
        try:
            response = self.s3.list_objects_v2(
            Bucket=self.bucket,
            Prefix = 'conversions/'
            )

            if 'Contents' not in response:
                print("✅ No files to check")
                return  0

            print(f"Found {len(response['Contents'])} files")

            #file list:
            files = response['Contents']

            newest_file = max(files, key=lambda x: x['LastModified'])
            print(f"The newest file is {newest_file['Key']} , last modified :{newest_file['LastModified']}.")
            
            return newest_file['Key']

        except Exception as e:
            print(f"❌Error: {e}")

   
    def get_conversion_stats(self):
        """ CONVERSION STATS """

        #get all the conversions
        conversions = self.get_all_conversions()

        #check if there are any 
        if not conversions:
            print("\n📭 No conversions in S3 yet")
            return

        # how many conversions
        how_many_conv = len(conversions)
            
        # Pair of currency conversion that was most common
        
        #extract pair from conversions 
        lista = [f"{item['from_currency']}->{item['to_currency']}"for item in conversions]
    
        #counting the pairs:
        count = Counter(lista)
        print(f"Counted pair: {count}") # Counter({('GBP', 'USD'): 10, ('USD', 'PLN'): 9})

        #most common pair:
        most_common = count.most_common(1)[0] #
        print("Most common pair: ", most_common) # (('GBP', 'USD'), 10)

        # total amount
        total = sum(item['amount'] for item in conversions)
        print("Total sum of amount: ", total)
        
        # mean amount
        #average = total / how_many_conv -> lepiej tak czy lepiej importowac statistics? 
        average = statistics.mean(item['amount'] for item in conversions)
        # max amount 
        max_amount = max(item['amount'] for item in conversions)
        # min amount
        min_amount = min(item['amount'] for item in conversions)

        #do rozwazenia zmiana na :
        #highest = max(conversions, key=lambda x: x['amount'])
        #lowest = min(conversions, key=lambda x: x['amount'])


        #output:
        print("📊 CONVERSION STATISTICS")
        print("=" * 50)
        print(f"Total conversions: {how_many_conv}")
        print(f"Most popular pair: {most_common}")
        print(f"Total amount: {total}")
        print(f"Average amount: ", f"{average:.2f}")
        print(f"Highest amount: ", max_amount)
        print(f"Lowest amount: ", min_amount)
 
    def remove_duplicate_conversions(self):
        
        
        try:
            #1 - get the files
            print(f"Reading from bucket {self.bucket}")

            response = self.s3.list_objects_v2(
                Bucket = self.bucket,
                Prefix = 'conversions/'
            )
            #check if any
            if 'Contents' not in response:
                print("⚠️ No files in conversions/ folder")
                return []

            files = response['Contents']
            print(f"Found {len(files)} files")

            #get the content of each file
            file_data = []

            for file in files:
                #get file from bucket, key = file name
                file_obj = self.s3.get_object(
                        Bucket = self.bucket,
                        Key = file['Key']
                    )
                #read content 
                content = file_obj['Body'].read().decode('utf-8')
                data = json.loads(content)
                
                # save the content to  file_data
                
               
                file_data.append({
                    'key': file['Key'], #file name
                    'last_modified': file['LastModified'], #last modification
                    'from_currency': data['from_currency'],
                    'to_currency': data['to_currency'],
                    'amount': data['amount'],
                    'rate': data['rate']
                })

            print(f"Get the contents of {len(file_data)} files.")

            #group by: (from, to, amount, rate)
            groups = defaultdict(list)

            #file list:
            
            for file_info in file_data:
                #signature -> combination of from, to, amount, rate
                signature = (
                    file_info['from_currency'],
                    file_info['to_currency'],
                    file_info['amount'],
                    file_info['rate']
                )
                groups[signature].append(file_info)  
            
            print(f"Found {len(groups)} unique conversions")        
            
            
            #delete the duplicates
            deleted_count = 0

            for signature, file_list in groups.items():
                if len(file_list) > 1:
                    from_curr, to_curr, amount, rate = signature
                    print(f"Duplicates for {from_curr} -> {to_curr}, amount: {amount}, rate: {rate}")
                    print(f"   Found: {len(file_list)} files ")

                    #find the latest
                    newest = max(file_list, key = lambda x: x['last_modified'])
                    print(f"   Left: {newest['key']}")

                    #delete the rest
                    for file_info in file_list:
                        if file_info['key'] != newest['key']:
                            self.s3.delete_object(
                                Bucket = self.bucket,
                                Key = file_info['key']
                            )
                            print(f"    Deleted: {file_info['key']}")
                            deleted_count +=1

            print(f"\n Deleted {deleted_count} duplicates")


        except Exception as e:
            print(f"❌Error: {e}")

 #===== pandas methods=====
    def pandas_report(self):
        """Advanced Pandas Report"""
        conversions = self.get_all_conversions()
    
        if not conversions:
            print("📭 No data for report")
            return
    
        df = pd.DataFrame(conversions)
    
        # Konwersja timestamp na datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
        print("\n" + "="*70)
        print("📊 ADVANCED PANDAS REPORT")
        print("="*70)
    
        # 1. basic info
        print("\n1️⃣ BASIC INFO:")
        print(f"   Total conversions: {len(df)}")
        print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
        # 2. Top 5 currency pairs
        print("\n2️⃣ TOP 5 CURRENCY PAIRS:")
        df['pair'] = df['from_currency'] + ' → ' + df['to_currency']
        top_pairs = df['pair'].value_counts().head(5)
        print(top_pairs)
    
        # 3. Amount statistics
        print("\n3️⃣ AMOUNT STATISTICS:")
        print(df['amount'].describe())
    
        # 4. Amount sum per currency
        print("\n4️⃣ TOTAL AMOUNT BY FROM_CURRENCY:")
        print(df.groupby('from_currency')['amount'].agg(['sum', 'mean', 'count']))
    
        # 5. average rate by pair
        print("\n5️⃣ AVERAGE RATE BY PAIR:")
        print(df.groupby('pair')['rate'].mean().sort_values(ascending=False))
    
        # 6. Conversions per day
        print("\n6️⃣ CONVERSIONS PER DAY:")
        df['date'] = df['timestamp'].dt.date
        daily = df.groupby('date').size()
        print(daily)
    
        # 7. largest conversions
        print("\n7️⃣ TOP 3 LARGEST CONVERSIONS:")
        top3 = df.nlargest(3, 'amount')[['from_currency', 'to_currency', 'amount', 'result', 'timestamp']]
        print(top3.to_string(index=False))
    
        print("\n" + "="*70)

        #save report to S3
        report_data = self.pandas_report()
        filename = f"reports/{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"

        self.s3.put_object(
            Bucket=self.bucket,
            Key=filename,
            Body=json.dumps(report_data, indent=2)
        )

        print(f"✅ Saved to S3: {filename}")
        return filename

 # ===== PROGRAM RUN METHODS =====

    #show menu 
    def show_menu(self):
        print("\n" + "="*30)
        print("       CURRENCY CONVERTER")
        print("="*30)
        for key, (description,_) in self.menu.items():
            print(f"{key}. {description}")
        print("="*30)
 
    
    #program exit
    def exit(self):     
        print("👋Good Bye!")
        import sys
        sys.exit(0)


    #program run
    def run(self):
        """Main loop"""

        print("\nWelcome!")

        while True:
            self.show_menu()

            try:
                choice = int(input("\n Choose an option: "))

                #check if option exist:
                if choice not in self.menu:
                    print("Invalid! Choose from menu")
                    continue
                #exit
                if choice == 0:
                    print("\n Good Bye")
                    break

                #run selected method
                description, method = self.menu[choice]
                if method:
                    method()
            except ValueError:
                print("Choose correct number from menu")

            except KeyboardInterrupt:
                print("\n\n 👋Keyboard interrupt. Good Bye")
                break




#MAIN PROGRAM
     #NEEDS NEW API KEY AND BUCKET NAME VARIABLES

if __name__ == "__main__":
    calc = CurrencyConverterFull(
        'YOUR API KEY',
        'YOUR BUCKET NAME'
        ) 
    calc.run()