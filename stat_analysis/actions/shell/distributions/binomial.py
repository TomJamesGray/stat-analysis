class Binomial:
    def __init__(self,n,p):
        self.n = n
        self.p = p

    def __repr__(self):
        return "<Binomial distribution n={} p={}>".format(self.n,self.p)