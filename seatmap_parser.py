import xml.etree.ElementTree as ET
import json
import os

'''CHOOSE BEWTEEN THE FILES'''

#seatmapfile = 'seatmap1.xml'
#seatmapfile = 'seatmap2.xml'

try:
    fname = os.path.basename(seatmapfile) #Extracting file name for json parsed file
    fname = fname.split('.')[0]

    tree = ET.parse(seatmapfile) #xml.etree.ElementTree library to parse the xml file
    root = tree.getroot()

    seatmap_dict = {} #Dictionary from which json file will be create
    seatmap_dict = {
        'seatmap' : {}
        }

    row_number = None
    seat_id = None
    seat_price = None
    cabin_class = 'NOT SPECIFY' 
    seat_availability = None

    #Seatmap1.xml
    if root.find('.').tag == '{http://schemas.xmlsoap.org/soap/envelope/}Envelope':

        ns = {'ns':"http://www.opentravel.org/OTA/2003/05/common/"}
        
        row_dict = {}
        rows_list = []

        for row in root.findall('.//ns:RowInfo', ns):

            row_number = row.attrib['RowNumber']
            cabin_class = row.attrib['CabinType']

            seat_list = []
            for seat_info in row.findall('ns:SeatInfo', ns):

                column_number = seat_info.attrib['ColumnNumber']

                for seat in seat_info.findall('ns:Summary', ns):

                    seat_id = seat.attrib['SeatNumber']

                    seat_availability = seat.attrib['OccupiedInd']
                    if seat_availability == 'true':
                        seat_availability = 'Available'
                    elif seat_availability == 'false':
                        seat_availability = 'Occupied'

                features_list = ['Center','Aisle','Window']
                for seat_feature in seat_info.findall('ns:Features', ns):

                    if seat_feature.text in features_list:
                        seat_type = seat_feature.text
                    else:
                        pass

                for service in seat_info.findall('ns:Service', ns):

                    fee = service.find('ns:Fee', ns)
                    price = fee.attrib['Amount']
                    currency = fee.attrib['CurrencyCode']
                    seat_price = (price[0:2] + ' ' + currency)
                
                seat_dict = {
                    'seat_type': seat_type, 'seatId' : seat_id, 'seatPrice' : seat_price, 'cabinClass' : cabin_class, 
                    'availability' : seat_availability
                    }

                seat_list.append(seat_dict)

            row_dict[row_number] = seat_list

            rows_list.append(row_dict)
        
        seatmap_dict['seatmap'] = rows_list

    #seatmap2.xml       
    elif root.find('.').tag == '{http://www.iata.org/IATA/EDIST/2017.2}SeatAvailabilityRS':

        ns = {'ns':'http://www.iata.org/IATA/EDIST/2017.2'}

        rows_list = []

        for seatmaps in root.findall('ns:SeatMap', ns): 
            
            cabin = seatmaps.find('ns:Cabin', ns)
            
            row_dict = {}
            for row in cabin.findall('ns:Row', ns):
                
                cabin_layout = cabin.find('ns:CabinLayout',ns)
                row_number = (row.find('ns:Number',ns)).text

                seats_list = []
                for seat in row.findall('ns:Seat', ns):
                    
                    column = (seat.find('ns:Column', ns)).text

                    column_list = ['B','E']
                    if column not in column_list:

                        seat_id = row_number + column
                        for column_per_cabin in cabin_layout.findall('ns:Columns', ns):

                            if column == column_per_cabin.attrib['Position']:
                                seat_type = column_per_cabin.text
                        try: 
                            price_code = seat.find('ns:OfferItemRefs',ns)
                            cartes = root.find('ns:ALaCarteOffer', ns)
                            for carte in cartes.findall('ns:ALaCarteOfferItem', ns):

                                if price_code.text == carte.attrib['OfferItemID']:

                                    price_tag = carte.find('ns:UnitPriceDetail',ns)
                                    price_tag = price_tag.find('ns:TotalAmount',ns)
                                    seat_price = (price_tag.find('ns:SimpleCurrencyPrice',ns)).text +' '+ price_tag.find(
                                        'ns:SimpleCurrencyPrice',ns).attrib['Code']
                        except:
                                seat_price = None

                        for seat_feature in seat.findall('ns:SeatDefinitionRef', ns):
                            
                            airplane_data = root.find('ns:DataLists', ns)
                            airplane_data = airplane_data.find('ns:SeatDefinitionList', ns)

                            for airplane_features in airplane_data.findall('ns:SeatDefinition', ns):
                                
                                individual_feature = None
                                if seat_feature.text == airplane_features.attrib['SeatDefinitionID']:

                                    description = airplane_features.find('ns:Description', ns)
                                    individual_feature = (description.find('ns:Text',ns)).text
                                    
                                    if individual_feature == 'OCCUPIED' or individual_feature == 'AVAILABLE':
                                        seat_availability = individual_feature
                                    else:
                                        continue

                        seat_dict = {
                                'seat_type': seat_type, 'seatId' : seat_id, 'seatPrice' : seat_price, 'cabinClass' : cabin_class, 
                                'availability' : seat_availability
                                }

                        seats_list.append(seat_dict)
                    else:
                        continue 

                row_dict[row_number] = seats_list
            rows_list.append(row_dict)

        seatmap_dict['seatmap'] = rows_list    

    with open(f'{fname}_parsed.json', 'w') as f:
        json.dump(seatmap_dict, f, indent = 4)

except:
    print('XML format not found')

