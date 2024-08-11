import numpy as np 
import matplotlib.pyplot as plt 

from scipy.stats import uniform
from scipy.stats import multivariate_normal

np.random.seed(42)

class mh_gauss:
    def __init__(self, dim, K, num_samples, target_mu, target_sigma, target_pi, proposal_mu, proposal_sigma):
        #target params: p(x) = \sum_k pi(k) N(x; mu_k,Sigma_k)
        self.dim = dim 
        self.K = K 
        self.num_samples = num_samples
        self.target_mu = target_mu
        self.target_sigma = target_sigma 
        self.target_pi = target_pi 
        
        #proposal params: q(x) = N(x; mu, Sigma)
        self.proposal_mu = proposal_mu 
        self.proposal_sigma = proposal_sigma 
        
        #sample chain params
        self.n_accept = 0
        self.alpha = np.zeros(self.num_samples)
        self.mh_samples = np.zeros((self.num_samples, self.dim))

    def target_pdf(self, x):
        #p(x) = \sum_k pi(k) N(x; mu_k,Sigma_k)
        prob = 0
        for k in range(self.K):
            prob += self.target_pi[k]*\
                multivariate_normal.pdf(x,self.target_mu[:,k],self.target_sigma[:,:,k])
        #end for
        return prob

    def proposal_pdf(self, x, mu):
        #q(x) = N(x; mu, Sigma)
        return multivariate_normal.pdf(x, mu, self.proposal_sigma)

    def sample(self):
        #draw init sample from proposal
        #import pdb; pdb.set_trace()
        x_init = multivariate_normal.rvs(self.proposal_mu, self.proposal_sigma, 1)
        self.mh_samples[0,:] = x_init

        for i in range(self.num_samples-1):
            x_curr = self.mh_samples[i,:]
            x_new = multivariate_normal.rvs(x_curr, self.proposal_sigma, 1)

            #MH ratio
            self.alpha[i] = self.proposal_pdf(x_curr, x_new) / self.proposal_pdf(x_new, x_curr) #q(x|x')/q(x'|x)
            self.alpha[i] = self.alpha[i] * (self.target_pdf(x_new)/self.target_pdf(x_curr)) #alpha x p(x')/p(x)

            #MH acceptance probability
            r = min(1, self.alpha[i])
            u = uniform.rvs(loc=0, scale=1, size=1)
            if (u <= r):
                self.n_accept += 1
                self.mh_samples[i+1,:] = x_new  #accept
            else:
                self.mh_samples[i+1,:] = x_curr #reject
        #end for
        print("MH acceptance ratio: ", self.n_accept/float(self.num_samples))
  
if __name__ == "__main__":

    dim = 2
    K = 2
    num_samples = 5000 
    target_mu = np.zeros((dim,K))
    target_mu[:,0] = [4,0]
    target_mu[:,1] = [-4,0]
    target_sigma = np.zeros((dim, dim, K))
    target_sigma[:,:,0] = [[2,1],[1,1]]
    target_sigma[:,:,1] = [[1,0],[0,1]]
    target_pi = np.array([0.4, 0.6])

    proposal_mu = np.zeros((dim,1)).flatten()
    proposal_sigma = 10*np.eye(dim)

    mhg = mh_gauss(dim, K, num_samples, target_mu, target_sigma, target_pi, proposal_mu, proposal_sigma)
    mhg.sample()

    plt.figure()
    plt.scatter(mhg.mh_samples[:,0], mhg.mh_samples[:,1], label='MH samples')
    plt.grid(True); plt.legend()
    plt.title("Metropolis-Hastings Sampling of 2D Gaussian Mixture")
    plt.xlabel("X1"); plt.ylabel("X2")
    #plt.savefig("./figures/mh_gauss2d.png")
    plt.show()