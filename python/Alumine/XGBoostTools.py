#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 09:44:18 2019

@author: gratienj
"""
import numpy as np
import xgboost as xgb

def GridSearchOptim(params, gridsearch_params, xgtrain, num_boost_round, nfold, metric, early_stopping, ParName, min_mae):
    
#    min_mae = float("Inf")    
    
    nbParam = len(np.shape([gridsearch_params])) - 1
    
    if nbParam == 2:
        best_params = (params[ParName[0]],params[ParName[1]])
        for param1, param2 in gridsearch_params:       
            # Update our parameters
            params[ParName[0]] = param1
            params[ParName[1]] = param2
            # Run CV
            cv_results = xgb.cv(params, xgtrain, num_boost_round=num_boost_round, nfold=nfold, \
                                metrics={metric}, early_stopping_rounds=early_stopping )
            # Update best MAE
            mean_mae = cv_results['test-' + metric + '-mean'].min()
            if mean_mae < min_mae:
                min_mae = mean_mae
                best_params = (param1,param2)
        
        params[ParName[0]] = best_params[0]
        params[ParName[1]] = best_params[1]
    else:
        best_params = (params[ParName])
        for par in gridsearch_params :
            params[ParName] = par    
            # Run CV
            cv_results = xgb.cv(params,xgtrain,num_boost_round=num_boost_round, nfold=nfold,\
                                metrics={metric},early_stopping_rounds=early_stopping)
            # Update best score
            mean_mae = cv_results['test-' + metric + '-mean'].min()
            if mean_mae < min_mae:
                min_mae = mean_mae
                best_params = par
                
        params[ParName] = best_params

    return params, min_mae


def OptimizeParams(Init_Params, nfold, early_stopping, num_boost_round, metric, LearningData, LearningTarget):
    
    xgb_model = xgb.XGBRegressor(learning_rate = np.array( Init_Params['learning_rate'], dtype=float),\
                                 n_estimators = np.array( Init_Params['n_estimators'], dtype=int),\
                                 max_depth = np.array(Init_Params['max_depth'], dtype=int),\
                                 
                                 min_child_weight = np.array( Init_Params['min_child_weight'], dtype=int),\
                                 gamma = np.array( Init_Params['gamma'], dtype=float),\
                                 subsample = np.array( Init_Params['subsample'], dtype=float),\
                                 colsample_bytree = np.array( Init_Params['colsample_bytree'], dtype=float),\
                                 scale_pos_weight = np.array(Init_Params['scale_pos_weight'], dtype=float),\
                                 
                                 reg_lambda = np.array( Init_Params['reg_lambda'], dtype=float), \
                                 reg_alpha = np.array( Init_Params['reg_alpha'], dtype=float), \
                                 seed = np.array( 42, dtype=int) , \
                                 nthread  = np.array(4, dtype=int))
    
    xgtrain = xgb.DMatrix(LearningData, LearningTarget)
        
    ###############################################################################
                    ## Optimisation de 'n_estimators' ##
    ###############################################################################
    params = xgb_model.get_params();

    cvresult = xgb.cv(params, xgtrain, num_boost_round=num_boost_round, nfold=nfold, \
                      metrics=metric, early_stopping_rounds=early_stopping)
        
    min_mae = cvresult['test-'  + metric + '-mean'].min()
    params['n_estimators'] = cvresult['test-'  + metric + '-mean'].idxmin()
    print("Best params for 'n_estimators': {} ---> Error : {}".format(params['n_estimators'], min_mae))
        
      
    ###############################################################################
        ## Optimisation des parametres 'max_depth' et 'min_child_weight' ##

    ###############################################################################
    ParName = ['max_depth', 'min_child_weight']

    gridsearch_params = [(max_depth, min_child_weight) for max_depth in range(2,11) for min_child_weight in range(1,7)]    
    params, min_mae = GridSearchOptim(params, gridsearch_params, xgtrain, num_boost_round, nfold, metric, early_stopping, ParName, min_mae)

    print("Best params for 'max_depth': {} and 'min_child_weight': {} ---> Error : {}".format(params[ParName[0]], params[ParName[1]], min_mae))
    
    ###############################################################################
        ## Optimisation des parametres 'subsample' et 'colsample' ##
    ###############################################################################
    ParName = ['subsample', 'colsample_bytree']

    gridsearch_params = [(subsample, colsample) for subsample in [i/10. for i in range(5,11)] for colsample in [i/10. for i in range(5,11)]]
    params, min_mae = GridSearchOptim(params, gridsearch_params, xgtrain, num_boost_round, nfold, metric, early_stopping, ParName, min_mae)

    print("Best params for 'subsample': {} and 'colsample_bytree': {} ---> Error : {}".format(params[ParName[0]], params[ParName[1]], min_mae))
        
    
    ###############################################################################
                    ## Optimisation du parametre 'gamma' ##
    ###############################################################################
    ParName = 'gamma'
    
    gridsearch_params = [i/10. for i in range(0,11)]
    params, min_mae = GridSearchOptim(params, gridsearch_params, xgtrain, num_boost_round, nfold, metric, early_stopping, ParName, min_mae)

    print("Best params for 'gamma': {} ---> Error : {}".format(params[ParName], min_mae))
        
    ###############################################################################
        ## Optimisation du parametre 'reg_lambda' et 'reg_alpha' ##
    ###############################################################################

    ParName = ['reg_lambda', 'reg_alpha']

    gridsearch_params = [(reg_lambda, reg_alpha) for reg_lambda in [i/10. for i in range(0,11)] for reg_alpha in [i/10. for i in range(0,11)]]
    params, min_mae = GridSearchOptim(params, gridsearch_params, xgtrain, num_boost_round, nfold, metric, early_stopping, ParName, min_mae)

    print("Best params for 'reg_lambda': {} and 'reg_alpha': {} ---> Error : {}".format(params[ParName[0]], params[ParName[1]], min_mae))
 
    
    ###############################################################################
                ## Optimisation du parametre 'learning_rate' ##
    ###############################################################################
    
    ParName = 'learning_rate'
    
    gridsearch_params = [.3, .2, .1, .05, .04, .03, .02, .01, .005]
    params, min_mae = GridSearchOptim(params, gridsearch_params, xgtrain, num_boost_round, nfold, metric, early_stopping, ParName, min_mae)

    print("Best params for 'learning_rate': {} ---> Error : {}".format(params[ParName], min_mae))
 

    return params



def computeXGBParam(LearningData, LearningTarget):
    Init_Params = {
        'learning_rate' : 0.1,
        'n_estimators' : 500,
        'max_depth': 5,
        'min_child_weight' : 1,
        'gamma' : 0,
        'subsample' : 0.8,
        'colsample_bytree' : 0.8,
        'scale_pos_weight' : 1,
        'reg_lambda' : 1,
        'reg_alpha' : 0,
        "booster":"gbtree"
        }


    params = {}
    Eta_n0 = Init_Params['learning_rate']
    Eta_n1 = 0
 
    metric = 'mae'

    nfold = 10
    early_stopping = 10
    num_boost_round = 1000
   
    while Eta_n0 != Eta_n1:
        Eta_n0 = Init_Params['learning_rate']
        params = OptimizeParams(Init_Params, nfold, early_stopping, num_boost_round, metric, LearningData, LearningTarget)
        Eta_n1 = params['learning_rate']
        Init_Params = params
    return params