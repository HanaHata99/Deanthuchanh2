import platform
from .web_utils import Utils

def get_database_pass():
    system = platform.system()
    if 'Darwin' == system:
        return '12345'
    else:
        return '12345'

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

    def sales_by_beertype(self):
        sql = '''
            SELECT  SUM("Total_Sales") AS sale,
                    "Beer_Style"
            FROM    dulieudean
            GROUP BY "Beer_Style"
            ORDER BY SALE DESC
        '''
        details = Utils.execute_sql(sql)

        sale_bts = []
        beer_styles = []
        for detail in details:
            sale_bts.append(detail.sale)
            beer_styles.append(detail.Beer_Style)
        
        return sale_bts, beer_styles
    
    def sales_by_location(self):
        sql = '''
            SELECT  SUM("Total_Sales") AS sale,
                    "Location"
            FROM    dulieudean
            GROUP BY "Location"
            ORDER BY SALE DESC
        '''
        details = Utils.execute_sql(sql)

        sale_locations = []
        locations = []
        for detail in details:
            sale_locations.append(detail.sale)
            locations.append(detail.Location)
        
        return sale_locations, locations

    def sales_by_month(self):
        sql = '''
            SELECT  SUM("Total_Sales") AS SALE,
                    DATE_PART('month', "Brew_Date")::int AS MNT
            FROM    dulieudean
            GROUP BY DATE_PART('month', "Brew_Date")
            ORDER BY MNT
        '''
        details = Utils.execute_sql(sql)

        sales = []
        months = []
        for detail in details:
            sales.append(detail.sale)
            months.append(detail.mnt)

        return (sales, months)

    def loss_ratio(self):
        sql = '''
            SELECT  AVG("Loss_During_Brewing") AS Loss_During_Brewing,
                    AVG("Loss_During_Fermentation") AS Loss_During_Fermentation,
                    AVG("Loss_During_Bottling_Kegging") AS Loss_During_Bottling_Kegging
            FROM dulieudean
        '''
        data = Utils.execute_sql_arow(sql)
        return (data.loss_during_brewing, data.loss_during_fermentation, data.loss_during_bottling_kegging)

    def quality_score(self):
        sql= '''
            SELECT  "Beer_Style",
                    AVG("Quality_Score") AS quality_score
            FROM    dulieudean
            GROUP BY "Beer_Style"
            ORDER BY quality_score DESC
        '''
        details = Utils.execute_sql(sql)
        quality_scores = []
        beer_styles = []
        for detail in details:
            quality_scores.append(detail.quality_score)
            beer_styles.append(detail.Beer_Style)

        return (quality_scores, beer_styles)