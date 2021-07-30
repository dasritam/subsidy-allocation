import numpy as np


def gen_popn(N=10000, c_min=10, a=5):
    c = np.random.poisson(2*np.log(10), size=(N, 1)) * c_min + c_min
    u = np.random.exponential(0.4, size=(N, 1)) * \
        c_min**2  # np.zeros(shape=(N, 1))
    mu = a*u * np.exp(np.divide(-u, a))
    mu[u < a] = a**2/np.e
    beta = np.random.uniform(np.zeros((N, 1)), c*u/mu)
    beta[u == 0] = np.random.uniform(np.zeros((N, 1)), c/mu)[u == 0]
    psi = beta*mu/c
    psi[u != 0] = (beta*mu/(u*c))[u != 0]
    popn = np.column_stack((u, c, mu, beta, psi))
    return popn

