import numpy as np
import timeit
import time
from scipy.io import loadmat
from scipy.optimize import minimize
from sklearn.metrics import confusion_matrix
from sklearn.svm import SVC


def preprocess():
    """
     Input:
     Although this function doesn't have any input, you are required to load
     the MNIST data set from file 'mnist_all.mat'.

     Output:
     train_data: matrix of training set. Each row of train_data contains
       feature vector of a image
     train_label: vector of label corresponding to each image in the training
       set
     validation_data: matrix of training set. Each row of validation_data
       contains feature vector of a image
     validation_label: vector of label corresponding to each image in the
       training set
     test_data: matrix of training set. Each row of test_data contains
       feature vector of a image
     test_label: vector of label corresponding to each image in the testing
       set
    """

    mat = loadmat('mnist_all.mat')  # loads the MAT object as a Dictionary

    n_feature = mat.get("train1").shape[1]
    n_sample = 0
    for i in range(10):
        n_sample = n_sample + mat.get("train" + str(i)).shape[0]
    n_validation = 1000
    n_train = n_sample - 10 * n_validation

    # Construct validation data
    validation_data = np.zeros((10 * n_validation, n_feature))
    for i in range(10):
        validation_data[i * n_validation:(i + 1) * n_validation, :] = mat.get("train" + str(i))[0:n_validation, :]

    # Construct validation label
    validation_label = np.ones((10 * n_validation, 1))
    for i in range(10):
        validation_label[i * n_validation:(i + 1) * n_validation, :] = i * np.ones((n_validation, 1))

    # Construct training data and label
    train_data = np.zeros((n_train, n_feature))
    train_label = np.zeros((n_train, 1))
    temp = 0
    for i in range(10):
        size_i = mat.get("train" + str(i)).shape[0]
        train_data[temp:temp + size_i - n_validation, :] = mat.get("train" + str(i))[n_validation:size_i, :]
        train_label[temp:temp + size_i - n_validation, :] = i * np.ones((size_i - n_validation, 1))
        temp = temp + size_i - n_validation

    # Construct test data and label
    n_test = 0
    for i in range(10):
        n_test = n_test + mat.get("test" + str(i)).shape[0]
    test_data = np.zeros((n_test, n_feature))
    test_label = np.zeros((n_test, 1))
    temp = 0
    for i in range(10):
        size_i = mat.get("test" + str(i)).shape[0]
        test_data[temp:temp + size_i, :] = mat.get("test" + str(i))
        test_label[temp:temp + size_i, :] = i * np.ones((size_i, 1))
        temp = temp + size_i

    # Delete features which don't provide any useful information for classifiers
    sigma = np.std(train_data, axis=0)
    index = np.array([])
    for i in range(n_feature):
        if (sigma[i] > 0.001):
            index = np.append(index, [i])
    train_data = train_data[:, index.astype(int)]
    validation_data = validation_data[:, index.astype(int)]
    test_data = test_data[:, index.astype(int)]

    # Scale data to 0 and 1
    train_data /= 255.0
    validation_data /= 255.0
    test_data /= 255.0

    return train_data, train_label, validation_data, validation_label, test_data, test_label


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def blrObjFunction(initialWeights, *args):
    """
    blrObjFunction computes 2-class Logistic Regression error function and
    its gradient.

    Input:
        initialWeights: the weight vector (w_k) of size (D + 1) x 1
        train_data: the data matrix of size N x D
        labeli: the label vector (y_k) of size N x 1 where each entry can be either 0 or 1 representing the label of corresponding feature vector

    Output:
        error: the scalar value of error function of 2-class logistic regression
        error_grad: the vector of size (D+1) x 1 representing the gradient of
                    error function
    """
    train_data, labeli = args

    n_data = train_data.shape[0]
    n_features = train_data.shape[1]
    error = 0
    error_grad = np.zeros((n_features + 1, 1))

    ##################
    # YOUR CODE HERE #
    ##################
    # HINT: Do not forget to add the bias term to your input data

    # Adding bias
    bias = np.ones((n_data, 1))
    new_features = n_features + 1
    weight = initialWeights.reshape((new_features, 1))

    # Adding bias at the beginning of the feature vector
    train_data = np.hstack((bias, train_data))

    theta_n = sigmoid(np.dot(train_data, weight))

    # Yn * log(theta_n)
    A = labeli * np.log(theta_n)

    # (1-Yn) * log(1-theta_n)
    B = (1.0 - labeli) * np.log(1.0 - theta_n)
    N = theta_n.shape[0]

    # EW = (-1/N0 ln p(yjw)
    error = (-1.0 / N) * np.sum(A+B)

    # DeltaEW = (1/N) * SIGMA (theta_n - yn) * xn
    error_grad = (1.0 / N) * np.sum(((theta_n - labeli) * train_data), axis = 0)

    return error, error_grad


def blrPredict(W, data):
    """
     blrObjFunction predicts the label of data given the data and parameter W
     of Logistic Regression

     Input:
         W: the matrix of weight of size (D + 1) x 10. Each column is the weight
         vector of a Logistic Regression classifier.
         X: the data matrix of size N x D

     Output:
         label: vector of size N x 1 representing the predicted label of
         corresponding feature vector given in data matrix

    """
    label = np.zeros((data.shape[0], 1))

    ##################
    # YOUR CODE HERE #
    ##################
    # HINT: Do not forget to add the bias term to your input data

    N = data.shape[0]
    bias = np.ones((N, 1))
    data = np.hstack((bias, data))
    WTX = np.dot(data, W)
    R = sigmoid(WTX)
    label = np.argmax(R, axis = 1)
    label = label.reshape((data.shape[0], 1))

    return label

def mlrObjFunction(params, *args):
    """
    mlrObjFunction computes multi-class Logistic Regression error function and
    its gradient.

    Input:
        initialWeights_b: the weight vector of size (D + 1) x 10
        train_data: the data matrix of size N x D
        labeli: the label vector of size N x 1 where each entry can be either 0 or 1
                representing the label of corresponding feature vector

    Output:
        error: the scalar value of error function of multi-class logistic regression
        error_grad: the vector of size (D+1) x 10 representing the gradient of
                    error function
    """
    train_data, labeli = args
    n_data = train_data.shape[0]
    n_feature = train_data.shape[1]
    error = 0
    error_grad = np.zeros((n_feature + 1, n_class))

    ##################
    # YOUR CODE HERE #
    ##################
    # HINT: Do not forget to add the bias term to your input data
    new_features = n_feature + 1
    w = params.reshape(new_features, n_class)

    bias = np.ones((n_data, 1))
    # Adding bias at the beginning of the feature vector
    X = np.hstack((bias, train_data))

    A = np.exp(np.dot(X, w))
    B = np.sum(np.exp(np.dot(X, w)), axis = 1).reshape(n_data, 1)

    theta = A / B

    # E(w) = SIGMA SIGMA ynk ln nk
    error = -1 * np.sum(np.sum(labeli * np.log(theta)))

    T = (theta - labeli)

    error_grad = np.dot(X.T, T)

    error = error / n_data
    error_grad = error_grad / n_data

    return error, error_grad.flatten()


def mlrPredict(W, data):
    """
     mlrObjFunction predicts the label of data given the data and parameter W
     of Logistic Regression

     Input:
         W: the matrix of weight of size (D + 1) x 10. Each column is the weight
         vector of a Logistic Regression classifier.
         X: the data matrix of size N x D

     Output:
         label: vector of size N x 1 representing the predicted label of
         corresponding feature vector given in data matrix

    """
    label = np.zeros((data.shape[0], 1))

    ##################
    # YOUR CODE HERE #
    ##################
    # HINT: Do not forget to add the bias term to your input data

    N = data.shape[0]
    bias = np.ones((N, 1))
    X = np.hstack((bias, data))
    WTX = np.dot(X, W)

    E = np.exp(WTX) / np.sum(np.exp(WTX))

    EN = E.shape[0]
    i = 0
    while i < EN:
        label[i] = np.argmax(E[i])
        i = i + 1
    label = label.reshape(label.shape[0], 1)

    return label


"""
Script for Logistic Regression
"""
train_data, train_label, validation_data, validation_label, test_data, test_label = preprocess()

# number of classes
n_class = 10

# number of training samples
n_train = train_data.shape[0]

# number of features
n_feature = train_data.shape[1]

Y = np.zeros((n_train, n_class))
for i in range(n_class):
    Y[:, i] = (train_label == i).astype(int).ravel()

# start = timeit.default_timer()
# Logistic Regression with Gradient Descent
W = np.zeros((n_feature + 1, n_class))
initialWeights = np.zeros((n_feature + 1, 1))
opts = {'maxiter': 100}
for i in range(n_class):
    labeli = Y[:, i].reshape(n_train, 1)
    args = (train_data, labeli)
    # print('\n Class')
    nn_params = minimize(blrObjFunction, initialWeights, jac=True, args=args, method='CG', options=opts)
    W[:, i] = nn_params.x.reshape((n_feature + 1,))

# Find the accuracy on Training Dataset
predicted_label = blrPredict(W, train_data)
print('\n Training set Accuracy:' + str(100 * np.mean((predicted_label == train_label).astype(float))) + '%')
# print(confusion_matrix(train_label, predicted_label, labels = [0,1,2,3,4,5,6,7,8,9]))

# Find the accuracy on Validation Dataset
predicted_label = blrPredict(W, validation_data)
print('\n Validation set Accuracy:' + str(100 * np.mean((predicted_label == validation_label).astype(float))) + '%')
# print(confusion_matrix(validation_label, predicted_label, labels = [0,1,2,3,4,5,6,7,8,9]))

# Find the accuracy on Testing Dataset
predicted_label = blrPredict(W, test_data)
print('\n Testing set Accuracy:' + str(100 * np.mean((predicted_label == test_label).astype(float))) + '%')
# print(confusion_matrix(test_label, predicted_label, labels = [0,1,2,3,4,5,6,7,8,9]))

# stop = timeit.default_timer()
# print(stop - start)

"""
Script for Support Vector Machine
"""

print('\n\n--------------SVM-------------------\n\n')
##################
# YOUR CODE HERE #
##################

## SVM with linear kernel ##
print('SVM with linear kernel')
timer = time.time()
svm = SVC(kernel='linear')
svm.fit(train_data, train_label.flatten())
print('\n Training data Accuracy:' + str(100*svm.score(train_data, train_label)) )
print('\n Validation data Accuracy:' + str(100*svm.score(validation_data, validation_label)) )
print('\n Testing data Accuracy:' + str(100*svm.score(test_data, test_label)) )
getTime = time.time() - timer
print('\n Time: ' + str(getTime) + ' seconds')

## SVM with radial basis function, gamma = 1 ##
print('\n\n SVM with radial basis function, gamma = 1')
timer = time.time()
svm = SVC(kernel='rbf', gamma=1.0)
svm.fit(train_data, train_label.flatten())
print('\n Training data Accuracy:' + str(100*svm.score(train_data, train_label)))
print('\n Validation data Accuracy:' + str(100*svm.score(validation_data, validation_label)))
print('\n Testing data Accuracy:' + str(100*svm.score(test_data, test_label)))
getTime = time.time() - timer
print('\n Time: ' + str(getTime) + ' seconds to complete')

## SVM with radial basis function, gamma = 0 ##
print('\n\n SVM with radial basis function, gamma = 0')
timer = time.time()
svm = SVC(kernel='rbf')
svm.fit(train_data, train_label.flatten())
print('\n Training data Accuracy:' + str(100*svm.score(train_data, train_label)))
print('\n Validation data Accuracy:' + str(100*svm.score(validation_data, validation_label)) )
print('\n Testing data Accuracy:' + str(100*svm.score(test_data, test_label)) )
getTime = time.time() - timer
print('\n Time: ' + str(getTime) + ' seconds to complete')


## SVM with radial basis function, different values of C ##
print('\n\n SVM with radial basis function, different values of C')
timer = time.time()
trainingAccuracy = np.zeros(11)
validationAccuracy = np.zeros(11)
testingAccuracy = np.zeros(11)
cValues = [1.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]

### for every C, train and compute accuracy ###
for i in range(11):
    print('\n C value: ' + str(cValues[i]))

    svm = SVC(C=cValues[i],kernel='rbf')
    svm.fit(train_data, train_label.flatten())

    trainingAccuracy[i] = 100*svm.score(train_data, train_label)
    print('\n Training data Accuracy:' + str(trainingAccuracy[i]))

    validationAccuracy[i] = 100*svm.score(validation_data, validation_label)
    print('\n Validation data Accuracy:' + str(validationAccuracy[i]))

    testingAccuracy[i] = 100*svm.score(test_data, test_label)
    print('\n Testing data Accuracy:' + str(testingAccuracy[i]))

getTime = time.time() - timer
print('\n Time: ' + str(getTime) + ' seconds to complete')


"""
Script for Extra Credit Part
"""
# start = timeit.default_timer()
# FOR EXTRA CREDIT ONLY
W_b = np.zeros((n_feature + 1, n_class))
initialWeights_b = np.zeros((n_feature + 1, n_class))
opts_b = {'maxiter': 100}

args_b = (train_data, Y)
nn_params = minimize(mlrObjFunction, initialWeights_b, jac=True, args=args_b, method='CG', options=opts_b)
W_b = nn_params.x.reshape((n_feature + 1, n_class))

# Find the accuracy on Training Dataset
predicted_label_b = mlrPredict(W_b, train_data)
print('\n Training set Accuracy:' + str(100 * np.mean((predicted_label_b == train_label).astype(float))) + '%')
# print(confusion_matrix(train_label, predicted_label_b, labels = [0,1,2,3,4,5,6,7,8,9]))

# Find the accuracy on Validation Dataset
predicted_label_b = mlrPredict(W_b, validation_data)
print('\n Validation set Accuracy:' + str(100 * np.mean((predicted_label_b == validation_label).astype(float))) + '%')
# print(confusion_matrix(validation_label, predicted_label_b, labels = [0,1,2,3,4,5,6,7,8,9]))

# Find the accuracy on Testing Dataset
predicted_label_b = mlrPredict(W_b, test_data)
print('\n Testing set Accuracy:' + str(100 * np.mean((predicted_label_b == test_label).astype(float))) + '%')
# print(confusion_matrix(test_label, predicted_label_b, labels = [0,1,2,3,4,5,6,7,8,9]))

# stop = timeit.default_timer()
# print(stop - start)
