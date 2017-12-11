def guess_d_type(sample):
    """
    Tries to guess the data type that should be used for the column and where
    necessary the structure of that data type such as DD/MM/YYYY for dates
    :param sample: A list of the values for that column, can be of any length
    :return: Tuple with d_type name and a reference to a lambda that converts the
    imported string to the chosen data type
    """
    probs = {
        "int":1.0,
        "float":1.0,
        "datetime":1.0,
        "string":1.0
    }
    convert_maps = {
        "int":lambda x:int(x),
        "float":lambda x:float(x),
        "string":lambda x:str(x),
        "datetime":lambda x:str(x)
    }
    for val in sample:
        points = 0
        numbers = 0
        others = 0
        date_time_chars = 0
        for c in val:
            if c == ".":
                points += 1
            elif c in ["0","1","2","3","4","5","6","7","8","9"]:
                numbers += 1
            elif c in [":","/","-","_"]:
                date_time_chars += 1
            else:
                others += 1
        if points == 1 and numbers == len(val)-1:
            probs["float"] *= 1.5
            probs["string"] *= 0.5

        if others == 0 and date_time_chars == 0:
            if int(float(val)) == float(val):
                probs["int"] *= 1.2
                probs["float"] *= 0.9
            elif float(val) != int(float(val)):
                probs["float"] *= 1.2
                probs["int"] *= 0.6

        if val[0] == "0" and len(val) == numbers:
            # Probably a phone number?
            probs["string"] *= 1.3

        if len(val) < 20 and date_time_chars >= 1:
            probs["datetime"] *= 1.5

        if others == len(val):
            probs["string"] *= 1.5
        elif others > 0:
            probs["string"] *= 1.05

        print(probs)

    # Return maximum value
    chosen_type = max(probs,key=probs.get)
    return (chosen_type, convert_maps[chosen_type])