# weight is measured in kg and height in m
def bmi_calc(weight, height):
    return weight / height 

# weight is measured in pounds here
def maintenace_cal(weight):
    return weight * 15

# made for losing body fat
def cut_cal(weight):
    return (weight * 15) - 500

# made if user wants to gain weight 
def bulk_cal(weight):
    return (weight * 15) + 500