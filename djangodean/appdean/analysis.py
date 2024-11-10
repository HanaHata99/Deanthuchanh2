import platform
import pgsql
import pandas as pd


def get_database_pass():
    system = platform.system()
    if 'Darwin' == system:
        return '12345'
    else:
        return '24032003'

class AnalysisData:
    def __init__(self) -> None:
        pass

    @staticmethod
    def convert(row):
        return {
            "batch_id": row.batch_id,
            "Brew_Date": row.Brew_Date,
            "Beer_Style": row.Beer_Style,
            "SKU": row.SKU,
            "Location": row.Location,
            "Fermentation_Time": row.Fermentation_Time,
            "Temperature": row.Temperature,
            "pH_Level": row.pH_Level,
            "Gravity": row.Gravity,
            "Alcohol_Content": row.Alcohol_Content,
            "Bitterness": row.Bitterness,
            "Color": row.Color,
            "Ingredient_Ratio": row.Ingredient_Ratio,
            "Volume_Produced": row.Volume_Produced,
            "Total_Sales": row.Total_Sales,
            "Quality_Score": row.Quality_Score,
            "Brewhouse_Efficiency": row.Brewhouse_Efficiency,
            "Loss_During_Brewing": row.Loss_During_Brewing,
            "Loss_During_Fermentation": row.Loss_During_Fermentation,
            "Loss_During_Bottling_Kegging": row.Loss_During_Bottling_Kegging
        }

    def get_dataframe(self):
        return self.dulieu
    
    def sales_by_month(self):
        sql= '''
            SELECT  SUM("Total_Sales") AS SALE,
                    DATE_PART('month', "Brew_Date")::int AS MNT
            FROM    dulieudean
            GROUP BY DATE_PART('month', "Brew_Date")
            ORDER BY MNT
        '''
        details = []
        with pgsql.Connection(("localhost", 5432), "postgres", get_database_pass(), "postgres", tls = False) as db:
            with db.prepare(sql) as statement:
                details = list(statement())
        
        sales = []
        months = []
        for detail in details:
            sales.append(detail.sale)
            months.append(detail.mnt)

        return (sales, months)

    def batch_by_month(self):
        sql= '''
            SELECT  COUNT("batch_id") AS batch,
                    DATE_PART('month', "Brew_Date")::int AS MNT
            FROM    dulieudean
            GROUP BY DATE_PART('month', "Brew_Date")
            ORDER BY MNT
        '''
        details = []
        with pgsql.Connection(("localhost", 5432), "postgres", get_database_pass(), "postgres", tls = False) as db:
            with db.prepare(sql) as statement:
                details = list(statement())
        
        batchs = []
        months = []
        for detail in details:
            batchs.append(detail.batch)
            months.append(detail.mnt)

        return (batchs, months)
    
    def volumn_by_month(self):
        sql= '''
            SELECT  SUM("Volume_Produced") AS VOL,
                    DATE_PART('month', "Brew_Date")::int AS MNT
            FROM    dulieudean
            GROUP BY DATE_PART('month', "Brew_Date")
            ORDER BY MNT
        '''
        details = []
        with pgsql.Connection(("localhost", 5432), "postgres", get_database_pass(), "postgres", tls = False) as db:
            with db.prepare(sql) as statement:
                details = list(statement())
        
        volums = []
        months = []
        for detail in details:
            volums.append(detail.vol)
            months.append(detail.mnt)

        return (volums, months)


