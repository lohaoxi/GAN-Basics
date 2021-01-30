import pandas as pd 
import numpy as np
pd.options.display.float_format = "{:.10f}".format

class LifeTable():
    
    def __init__(self, csv_path):
        self.df = pd.read_csv(filepath_or_buffer = csv_path).fillna(0)
        self.df_ult = self.get_df_ult()
        self.df_sel0, self.df_sel1 = self.get_df_sel()
        
    def get_df_ult(self, round_up = True):

        l_ult = self.df["q_ult"]
        l_ult = l_ult.shift(1)
        l_ult = l_ult.fillna(0)
        l_ult = 1 - l_ult
        l_ult = l_ult.cumprod()
        l_ult = 10000 * l_ult

        if round_up == True: l_ult = round(l_ult, 4) 

        df_ult = {"x": self.df["x"], 
                  "l": l_ult}
        df_ult = pd.DataFrame(df_ult)

        return(df_ult)

    def get_df_sel(self, round_up = True):

        l_ult = get_df_ult(df = self.df, 
                           round_up = False)
        l_ult = l_ult["l"]
        l_ult_lead2 = l_ult.shift(-2).fillna(0)
        q_sel1_lead1 = self.df["q_sel1"].shift(-1).fillna(0)
        l_sel1 = l_ult_lead2 / (1 - q_sel1_lead1)
        l_sel0 = l_sel1 / (1 - self.df["q_sel0"])
        l_sel1 = l_sel1.shift(1).fillna(0)

        l_sel0 = round(l_sel0, 4)
        l_sel1 = round(l_sel1, 4)

        df_sel0 = {"x": self.df["x"], 
                   "l": l_sel0}

        df_sel1 = {"x": self.df["x"], 
                   "l": l_sel1}

        df_sel0 = pd.DataFrame(df_sel0)
        df_sel1 = pd.DataFrame(df_sel1)

        return(df_sel0, 
               df_sel1)
    
    def l_ult(self, x):
        df = self.df_ult
        l = df.loc[df['x'] == x].iloc[0, 1]
        return(l)
    
    def l_sel0(self, x):
        df = self.df_sel0
        l = df.loc[df['x'] == x].iloc[0, 1]
        return(l)
    
    def l_sel1(self, x):
        df = self.df_sel1
        l = df.loc[df['x'] == x].iloc[0, 1]
        return(l)
    
    def pxt_ult(self, x, t = 1, step = True, round_up = True):
        age_curr = x
        age_next = x + t
        l_x = self.l_ult(x = curr_age)
        l_xt = self.l_ult(x = next_age)
        pxt = l_xt / l_x
        pxt = round(pxt, 6) if round_up == True else pxt
        
        if step == True:            
            print("l{xt} = {l_xt}".format(xt = age_next, l_xt = l_xt))
            print("l{x} = {l_x}".format(x = age_curr, l_x = l_x))
            print("{t}p{x} = {pxt}".format(t = t if t != 1 else "", 
                                            x = x, 
                                            pxt = pxt))
        return(pxt)

    def qxt_ult(self, x, t = 1, m = 0, step = True, round_up = True):        
        qxt = self.pxt_ult(x = x, t = m, step = step, round_up = False) * (1 - self.pxt_ult(x = x + m, t = t, step = step, round_up = False))  
        
        qxt = round(qxt, 6) if round_up == True else qxt

        if step == True:            
            print("{m}|{t}q{x} = {qxt}".format(t = t if t != 1 else "", 
                                            m = m,
                                            x = x, 
                                            qxt = qxt))
        
        return(qxt)
    
    def pxt_sel(self, x, t = 1, r = 0, step = True, round_up = True):
        
        age_upper = x + r + t
        age_lower = x + r
        
        if r > 1:
            l_upper = self.l_ult
            l_lower = self.l_ult
        elif r == 1:
            l_upper = self.l_ult
            l_lower = self.l_sel1
        elif r == 0:
            l_lower = self.l_sel0
            if t > 1:
                l_upper = self.l_ult
            elif t == 1:
                l_upper = self.l_sel1
            elif t == 0:
                l_upper = self.l_sel0
        
        l_xrt = l_upper(age_upper)
        l_xr = l_lower(age_lower)
        pxt = l_xrt / l_xr
        pxt = round(pxt, 6) if round_up == True else pxt
        
        
        if step == True: 
                        
            print("l{xrt} = {l_xrt}".format(xrt = age_upper, l_xrt = l_xrt))
            print("l{xr} = {l_xr}".format(xr = age_lower, l_xr = l_xr))
            print("{t}p{x}+{r} = {pxt}".format(t = t if t != 1 else "", 
                                            r = r, 
                                            x = x, 
                                            pxt = pxt))

        return(pxt)
    
    def qxt_sel(self, x, t = 1, r = 0, m = 0, step = True, round_up = True):
        
        age_upper_a = x + r + m
        age_upper_b = x + r + t + m
        age_lower = x + r
        
        if r > 1:
            l_upper_a = self.l_ult
            l_upper_b = self.l_ult
            l_lower = self.l_ult
        elif r == 1:
            l_upper_a = self.l_sel1 if m == 0 else self.l_ult
            l_upper_b = self.l_ult
            l_lower = self.l_sel1
            
        elif r == 0:
            l_lower = self.l_sel0
            
            if m > 1:
                l_upper_a = self.l_ult
                l_upper_b = self.l_ult 
            if m == 1:
                l_upper_a = self.L_sel1
                l_upper_b = self.l_ult
            if m == 0:
                l_upper_a = self.l_sel0
                if t > 1:
                    l_upper_b = self.l_ult
                elif t == 1:
                    l_upper_b = self.l_sel1
                elif t == 0:
                    l_upper_b = self.l_sel0
        
        l_xrt = l_upper_a(age_upper_a)
        l_xrtm = l_upper_b(age_upper_b)
        l_xr = l_lower(age_lower)
        qxt = (l_xrt - l_xrtm) / l_xr
        qxt = round(qxt, 6) if round_up == True else qxt
        
        
        if step == True: 
                        
            print("l{xrt} = {l_xrt}".format(xrt = age_upper_a, l_xrt = l_xrt))
            print("l{xrtm} = {l_xrt}".format(xrtm = age_upper_b, l_xrt = l_xrtm))
            print("l{xr} = {l_xr}".format(xr = age_lower, l_xr = l_xr))
            print("{m}|{t}q{x}+{r} = {qxt}".format(t = t if t != 1 else "", 
                                            r = r, 
                                            m = m,
                                            x = x, 
                                            qxt = qxt))
        
        return(qxt)


        
        

