# Define the data types that can be used
# TODO implement format attributes for types like datetime
types = {
    "int":{
        "convert":lambda x:int(x)
    },
    "float":{
        "convert":lambda x:float(x)
    },
    "string":{
        "convert":lambda x:str(x)
    },
    "datetime":{
        "convert":lambda x,fmt:str(x),
        "format_required":True
    }
}