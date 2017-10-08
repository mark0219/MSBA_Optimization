#Optimization
#Homework 1
#Chaoran Zhang - Session 1


'''
#1. Linear Search
def linearSearch (A,target):
    for x in range(len(A)):
        if (A[x]==target):
            return A[x]
        #return False

num_list = [1,2,3,4,5,6,7,8,9,10]
num = 5
print linearSearch(num_list, num)


#2. Exhaustive Enumeration
from math import sqrt

def linearSearch_sqrt(N):
    epsilon = 0.001
    x = 0.000
    while x*x < N - epsilon:
        x += epsilon
    return '%.3f' % x

print linearSearch_sqrt(15)
print sqrt(15)


#3. Binary Search
def binarySearch(A, target):
    low = 0
    high = len(A) - 1
    while low <= high:
        mid = low + (high - low) / 2
        print "LOW {} HI {} MID {}, comparing {} to {}".format(low,high,mid,target,A[mid])
        if A[mid] == target:
            return mid
        if A[mid] > target:
            high = mid - 1
        else:
            low = mid + 1

F = range(32)
target = 4
print "Looking for [{}] in array {}".format(target,F)
print binarySearch (F,target)
'''

#5. Finding Kth Root
from math import sqrt

def bisection_search_kth_root(n, k):
    low = 0
    high = 1000000
    epsilon = 0.001
    while low <= high:
        mid = low + (high - low) / 2.0
        print "LOW {} HI {} MID {}, comparing {} to {}".format(low,high,mid,mid,n**(1/k))
        if abs(mid**k - n) <= epsilon:
            return '%.3f' % mid
            break
        if mid**k > n:
            high = mid
        else:
            low = mid
    return False

print bisection_search_kth_root(100, 2)
print sqrt(100)


#7. Argmax Constraint
from math import log

def bisection_search_biggest_n_factorial(n):
    low = 0
    high = 0.001
    epsilon = 0.001
    
    while True:
        if high*log(high,2)-high+1 < n:
            high = 2 * high
        else:
            break
        
    while low <= high:
        mid = low + (high - low) / 2.0
        if abs(mid*log(mid, 2) - mid + 1 - n) <= epsilon:
            return mid, high
        if mid*log(mid, 2) - mid + 1 > n:
            high = mid
        else:
            low = mid

print bisection_search_biggest_n_factorial(2**43)

'''
#8. Newton-Raphson
from math import sqrt

def newton_sqrt(k):
    epsilon = .001
    y = k / 2.0 #guess
    while abs(y*y-k) >= epsilon:
        y = y - (((y**2) - k)/(2*y))
    return '%.3f' % y

print newton_sqrt(55)
print sqrt(55)
'''