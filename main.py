import argparse

import numpy as np
import torch
from torch.utils.data import DataLoader

from src.data import load_data
from src.methods.dummy_methods import DummyClassifier
from src.methods.kmeans import KMeans
from src.methods.logistic_regression import LogisticRegression
from src.methods.svm import SVM
from src.utils import (
    normalize_fn,
    append_bias_term,
    accuracy_fn,
    macrof1_fn,
    KFold_cross_validation,
)


def main(args):
    """
    The main function of the script. Do not hesitate to play with it
    and add your own code, visualization, prints, etc!

    Arguments:
        args (Namespace): arguments that were parsed from the command line (see at the end
                          of this file). Their value can be accessed as "args.argument".
    """
    ## 1. First, we load our data and flatten the images into vectors
    xtrain, xtest, ytrain, ytest = load_data(args.data)
    print(xtrain[0])
    xtrain = xtrain.reshape(xtrain.shape[0], -1)
    xtest = xtest.reshape(xtest.shape[0], -1)

    ## 2. Then we must prepare it. This is where you can create a validation set,
    #  normalize, add bias, etc.
    if args.normalize:
        mean, std = xtrain.mean(axis=0), xtrain.std(axis=0)
        xtrain, xtest = normalize_fn(xtrain, mean, std), normalize_fn(xtest, mean, std)
    if args.append_bias:
        xtrain, xtest = append_bias_term(xtrain), append_bias_term(xtest)

    ### WRITE YOUR CODE HERE to do any other data processing
    np.random.seed(args.seed)

    # Dimensionality reduction (FOR MS2!)
    if args.use_pca:
        print("Using PCA")
        xtrain = xtrain.reshape(xtrain.shape[0], -1)
        xtest = xtest.reshape(xtest.shape[0], -1)
        pca_obj = PCA(d=args.pca_d)
        ### WRITE YOUR CODE HERE: use the PCA object to reduce the dimensionality of the data
        print(f'The total variance explained by the first {args.pca_d} principal components is {pca_obj.find_principal_components(xtrain):.3f} %')
        # perform dimension reduction on input data
        xtrain, xtest = pca_obj.reduce_dimension(xtrain), pca_obj.reduce_dimension(xtest)
    ## 3. Initialize the method you want to use.

    # Use NN (FOR MS2!)
    if args.method == "nn":
        raise NotImplementedError("This will be useful for MS2.")

    # Follow the "DummyClassifier" example for your methods
    if args.method == "dummy_classifier":
        method_obj = DummyClassifier(arg1=1, arg2=2)

    elif args.method == "kmeans":
        method_obj = KMeans(K=args.K, max_iters=args.max_iters)

    elif args.method == "logistic_regression":
        method_obj = LogisticRegression(lr=args.lr, max_iters=args.max_iters)

    elif args.method == "svm":
        method_obj = SVM(
            C=args.svm_c,
            kernel=args.svm_kernel,
            gamma=args.svm_gamma,
            degree=args.svm_degree,
            coef0=args.svm_coef0,
        )

    # 4.0 Train and validate the method: k-fold validation
    if not args.test:
        KFold_cross_validation(xtrain, ytrain, args.k_fold, method_obj)
        return

    ## 4.1 Train and test the method

    # Fit (:=train) the method on the training data
    preds_train = method_obj.fit(xtrain, ytrain)

    # Predict on unseen data
    preds = method_obj.predict(xtest)

    ## Report results: performance on train and valid/test sets
    acc = accuracy_fn(preds_train, ytrain)
    macrof1 = macrof1_fn(preds_train, ytrain)
    print(f"\nTrain set: accuracy = {acc:.3f}% - F1-score = {macrof1:.6f}")

    acc = accuracy_fn(preds, ytest)
    macrof1 = macrof1_fn(preds, ytest)
    print(f"Test set:  accuracy = {acc:.3f}% - F1-score = {macrof1:.6f}")

    ### WRITE YOUR CODE HERE if you want to add other outputs, visualization, etc.


if __name__ == "__main__":
    # Definition of the arguments that can be given through the command line (terminal).
    # If an argument is not given, it will take its default value as defined below.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        default="dataset_HASYv2",
        type=str,
        help="the path to wherever you put the data, if it's in the parent folder, you can use ../dataset_HASYv2",
    )
    parser.add_argument(
        "--method",
        default="dummy_classifier",
        type=str,
        help="dummy_classifier / kmeans / logistic_regression / svm / nn (MS2)",
    )
    parser.add_argument(
        "--K", type=int, default=10, help="number of clusters for K-Means"
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=1e-5,
        help="learning rate for methods with learning rate",
    )
    parser.add_argument(
        "--max_iters",
        type=int,
        default=100,
        help="max iters for methods which are iterative",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="train on whole training data and evaluate on the test data, otherwise use a validation set",
    )
    parser.add_argument(
        "--svm_c", type=float, default=1.0, help="Constant C in SVM method"
    )
    parser.add_argument(
        "--svm_kernel",
        default="linear",
        help="kernel in SVM method, can be 'linear' or 'rbf' or 'poly'(polynomial)",
    )
    parser.add_argument(
        "--svm_gamma",
        type=float,
        default=1.0,
        help="gamma prameter in rbf/polynomial SVM method",
    )
    parser.add_argument(
        "--svm_degree", type=int, default=1, help="degree in polynomial SVM method"
    )
    parser.add_argument(
        "--svm_coef0", type=float, default=0.0, help="coef0 in polynomial SVM method"
    )

    # Feel free to add more arguments here if you need!
    parser.add_argument(
        "--seed", type=int, default=80, help="the numpy seed for the experiment"
    )
    parser.add_argument(
        "--valid_ratio", type=float, default=0.2, help="the ratio of validation set"
    )
    parser.add_argument("--k_fold", type=int, default=5, help="k-fold validation")
    parser.add_argument(
        "--append_bias", action="store_true", help="append bias to data"
    )
    parser.add_argument("--normalize", action="store_true", help="normalize data")

    # Arguments for MS2
    parser.add_argument("--use_pca", action="store_true", help="to enable PCA")
    parser.add_argument(
        "--pca_d", type=int, default=200, help="output dimensionality after PCA"
    )

    # "args" will keep in memory the arguments and their value,
    # which can be accessed as "args.data", for example.
    args = parser.parse_args()
    main(args)
