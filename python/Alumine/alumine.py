#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 09:57:43 2019

@author: gratienj
"""

import os
import glob
import numpy as np
import pandas as pd
import xgboost as xgb

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import math


def eval_func(xi,yi,x,istart=0):
    #print('yi',yi)
    nx=xi.shape[0]
    x_old=0.
    y_old=0.
    if istart>0 :
        x_old=xi[istart-1]
        y_old=yi[istart-1]
    for i in range(istart,nx):
        if xi[i]>x:
            fy=y_old
            if xi[i]>x_old:
                fy = fy+(x-x_old)*(yi[i]-y_old)/(xi[i]-x_old)
            #print('FY(',i,')',x_old,x,xi[i],y_old,fy,yi[i])
            return i,fy
        else:
            x_old=xi[i]
            y_old=yi[i]
    return i,y_old

def project_func(xi,yi,x):
    nxi=xi.shape[0]
    nx=x.shape[0]
    y=np.zeros([nx],dtype=float)
    istart=0
    for i in range(nx):
        istart,y[i]=eval_func(xi,yi,x[i],istart)
        #print('     y[',i,']=',y[i])
    return y

def tortuosityBinIndex(x,xmin,xmax,nbins):
    dx=(xmax-xmin)/nbins
    return math.floor((x-xmin)/dx)
            
def normalize(df,sp):
    for i in range(sp):
        xi='x'+str(i)
        meani=df[xi].mean()
        df[xi] = df[xi].apply(lambda yi : yi - meani)
    return df
    
def computeHystFeatures(x,y,x0,eps):
    nx=x.shape[0]
    ymax = 0.
    x0eps=0.
    x1eps=0.
    ysum = 0.;
    for i in range(nx):
        ymax = max(ymax,y[i])
        if x[i]>x0:
            ysum = ysum+y[i]
            if x0eps==0:
                if y[i]>eps:
                    x0eps=x[i]
            if y[i]>eps:
                x1eps=x[i]
    return (ymax,x1eps-x0eps,ysum/nx)
 
def affiche(px,df,n,suff=""):
    sp=len(px)
    min_tortuosity=df['TORTUOSITY'].min()
    max_tortuosity=df['TORTUOSITY'].max()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    jet = plt.get_cmap('jet') 
    cNorm  = colors.Normalize(vmin=min_tortuosity, vmax=max_tortuosity)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)

    lines = []
    for index,row in df.iterrows():
        if index > n:
            break
        #case=str(row[0])
        tortuosity=row[1]

        colorVal = scalarMap.to_rgba(tortuosity)
        colorText = (suff+'_df : (%4.2f)'%(tortuosity))
        retLine, = ax.plot(px,row[2:2+sp],color=colorVal,label=colorText)
        lines.append(retLine)
            
    handles,labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='upper left')

def afficheBase(px,base_x):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    lines = []
    retLine, = ax.plot(px,base_x[0][:],color='red',label='base0')
    lines.append(retLine)
    retLine, = ax.plot(px,base_x[1][:],color='blue',label='base1')
    lines.append(retLine)
    retLine, = ax.plot(px,base_x[2][:],color='green',label='base2')
    lines.append(retLine)            
    handles,labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='upper left')
    
def afficheNP(px,df,y,nindex,suff=""):
    
    min_y=y.min()
    max_y=y.max()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    jet = cm = plt.get_cmap('jet') 
    cNorm  = colors.Normalize(vmin=min_y, vmax=max_y)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)

    lines = []
    for index in range(nindex):
        tortuosity=y[index]

        colorVal = scalarMap.to_rgba(tortuosity)
        colorText = (suff+'_df : (%4.2f)'%(tortuosity))
        retLine, = ax.plot(px,df[index][:],color=colorVal,label=colorText)
        lines.append(retLine)
            
    handles,labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='upper left')

def afficheHyst(hyst_list,y,max_index,suff=""):
    
    min_y=y.min()
    max_y=y.max()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    jet = cm = plt.get_cmap('jet') 
    cNorm  = colors.Normalize(vmin=min_y, vmax=max_y)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)

    lines = []
    index = 0
    for hyst in hyst_list:
        if index>=max_index:
            break
        tortuosity=y[index]

        colorVal = scalarMap.to_rgba(tortuosity)
        colorText = (suff+'_hyst : (%4.2f)'%(tortuosity))
        retLine, = ax.plot(hyst[0],hyst[1],color=colorVal,label=colorText)
        lines.append(retLine)
        index=index+1
            
    handles,labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='upper left')

def plotHystFeature(features,y,nindex):
    from mpl_toolkits.mplot3d import Axes3D
    min_y=y.min()
    max_y=y.max()
    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')
    jet = plt.get_cmap('jet') 
    cNorm  = colors.Normalize(vmin=min_y, vmax=max_y)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
    xx = []
    yy = []
    zz = []
    cc = []
    index = 0
    for feature in features:
        tortuosity=y[index]
        colorVal = scalarMap.to_rgba(tortuosity)
        xx.append(features[index][0])
        yy.append(features[index][1])
        zz.append(features[index][2])
        cc.append(colorVal)
        index=index+1
    ax.scatter(xx,yy,zz,c=cc)
    ax.set_xlabel('YMAX')
    ax.set_ylabel('DXMAX')
    ax.set_zlabel('YAVG')

def computePCA(X,ncomp):
    import numpy as np
    from sklearn.decomposition import PCA
    pca = PCA(n_components=ncomp)
    new_x=pca.fit_transform(X)  
    print(pca.explained_variance_ratio_)  
    print(pca.singular_values_)
    return new_x,pca

def plotTrainTestCover(reducted_x_train,reducted_x_test):
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')
    xx = []
    yy = []
    zz = []
    cc = []
    for x in reducted_x_train:
        xx.append(x[0])
        yy.append(x[1])
        zz.append(x[2])
        cc.append('blue')
    for x in reducted_x_test:
        xx.append(x[0])
        yy.append(x[1])
        zz.append(x[2])
        cc.append('red')
        
    ax.scatter(xx,yy,zz,c=cc)
    ax.set_xlabel('C0')
    ax.set_ylabel('C1')
    ax.set_zlabel('C2')

def computeSVR(X,y):
    from sklearn.svm import SVR
    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)    
    clf = SVR(gamma='scale', C=1.0, epsilon=0.2)
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    y_predict = clf.predict(X_train)
    print("SCORE",score)

def compute_predict(clf,name,X_train, X_test, y_train, y_test):
    from sklearn.metrics import accuracy_score
    clf.fit(X_train, y_train)
    yy=clf.predict(X_test)

    score = clf.score(X_test, y_test)
    print("SCORE",name,score)
    accuracy = accuracy_score(y_test, yy)
    print("Accuracy: %.2f%%" % (accuracy * 100.0))
    yy_err = np.zeros([yy.shape[0]],dtype=float)
    for i in range(yy.shape[0]):
        yy_err[i] = abs(yy[i]-y_test[i])*2/(yy[i]+y_test[i])
    return yy,yy_err

def plotRegressionModelResults(model_name,y_test,y_pred,y_err):
    fig = plt.figure()
    plt.subplot(121)
    plt.hist(y_err,bins=20)
    plt.title('Histogram Err'+model_name)
    plt.subplot(122)
    plt.scatter(y_test,y_pred,color='red')
    plt.scatter(y_test,y_test,color='blue')
    plt.show()
    
def compute_xgb_predict(model_name,xgb_params,X_train, X_test, y_train, y_test):
    import xgboost as xgb
    import numpy as np
    from sklearn.metrics import accuracy_score
    model = xgb.XGBRegressor(\
          learning_rate    = np.array( xgb_params['learning_rate'], dtype=float), \
          n_estimators     = np.array( xgb_params['n_estimators'], dtype=int),\
          max_depth        = np.array( xgb_params['max_depth'], dtype=int),\
          min_child_weight = np.array( xgb_params['min_child_weight'], dtype=int),\
          gamma            = np.array( xgb_params['gamma'], dtype=float),\
          subsample        = np.array( xgb_params['subsample'], dtype=float),\
          colsample_bytree = np.array( xgb_params['colsample_bytree'], dtype=float),\
          reg_lambda       = np.array( xgb_params['reg_lambda'], dtype=float), \
          reg_alpha        = np.array( xgb_params['reg_alpha'], dtype=float), \
          seed             = np.array( 42, dtype=int) , \
          nthread          = np.array(4, dtype=int))
 
    metric = 'mae'

    Model = model.fit(X_train, y_train,eval_metric=metric)
    yy=Model.predict(X_test)

    score = Model.score(X_test, y_test)
    print("SCORE",model_name,score)
    accuracy = accuracy_score(y_test, yy)
    print("Accuracy: %.2f%%" % (accuracy * 100.0))
    xgb.plot_importance(model)
    yy_err = np.zeros([yy.shape[0]],dtype=float)
    for i in range(yy.shape[0]):
        yy_err[i] = abs(yy[i]-y_test[i])*2/(yy[i]+y_test[i])
    return yy,yy_err

def main():

    # INSERTING IMAGES IN DIRECTORY
    dataFolder='/work/irlin355_1/gratienj/BigData/DigitalSandBox/Data/Alumine'

    #with open(os.path.join(data_dir,'Output','output_training.csv'),'r') as f:
    tortuosity_file=os.path.join(dataFolder,'CSV_R11','tortuosity.xls')
    tortuosity_df=pd.read_excel(tortuosity_file,dtype={'ID':np.str,'TORTUOSITY':np.float})
    #tortuosity_df.plot.hist(bins=20)

    min_tortuosity=tortuosity_df['TORTUOSITY'].min()
    max_tortuosity=tortuosity_df['TORTUOSITY'].max()
    mean_tortuosity=tortuosity_df['TORTUOSITY'].mean()
    nb_samples = tortuosity_df.shape[0]
    print("NB SAMPLES",nb_samples)
    print('TORTUOSISITY MIN MAX AVG',min_tortuosity,max_tortuosity,mean_tortuosity)
    nbins=10
    max_binsize=50

    hist_index=np.zeros(nbins+1,dtype=int)

    
    sp=int(100)
    px=np.zeros([sp],dtype=float)
    dx=2./sp
    for i in range(sp):
        px[i]=(i+1)*dx
        xi='x'+str(i)
        tortuosity_df[xi]=0.
    py=np.zeros([nb_samples,sp],dtype=float)    

    hsp = int(sp/2)        
    hyst_px=np.zeros([hsp],dtype=float)
    for i in range(hsp):
        hyst_px[i]=(i+1)*dx    
    hyst_py=np.zeros([nb_samples,hsp],dtype=float)    

    #fig = plt.figure()
    #ax = fig.add_subplot(111)
    row_indexes = []
    row_ids = []
    rindex = 0
    hyst_curves = []
    hyst_features = []
    for index,row in tortuosity_df.iterrows():
        #if index>0:
        #    break
        case=str(row[0])
        tortuosity=row[1]

        bin_index = tortuosityBinIndex(tortuosity,min_tortuosity,max_tortuosity,nbins)
        if hist_index[bin_index] < max_binsize:
            print(index,'name',case,' TORTUOSITY ',tortuosity)
            
            hist_index[bin_index] = hist_index[bin_index] + 1
            row_indexes.append(index)
            row_ids.append(case)
            file=os.path.join(dataFolder,'CSV_R11',case+'.xls')
            df=pd.read_excel(file)
            def fx(x,x_old,hysteresis):
                if x<x_old:
                    hysteresis=True
                if hysteresis:
                    return True,2.-x
                else:
                    return False,x
            #df['pression_relative']=df['pression_relative'].apply(fx)
    
            hysteresis=False 
            x_old=0.
            hys_x = []
            hys_y = []
            nx=df.shape[0]
            hyst_x0 = max(df['pression_relative'][0],df['pression_relative'][nx-1])
            for i,df_row in df.iterrows():
                if df_row[0]>=hyst_x0:
                    hys_x.append(df_row[0])
                    hys_y.append(df_row[1])
                hysteresis,x=fx(df_row[0],x_old,hysteresis)
                #print("HYST",hysteresis,x,x_old,df_row[0],df_row[1])
                x_old=df_row[0]
                df['pression_relative'][i]=x
            hyst_curves.append((hys_x,hys_y))
            x=df['pression_relative']
            y=df['volume']
            
        
            #colorVal = scalarMap.to_rgba(tortuosity)
            #colorText = ('tortuosity : (%4.2f)'%(tortuosity))
            #retLine, = ax.plot(x,y,color=colorVal,label=colorText)
            #lines.append(retLine)
        
            ppy=project_func(x,y,px)
            py[rindex] = ppy
            rindex = rindex+1
            for j in range(sp):
                tortuosity_df.iloc[index,2+j] = ppy[j]

            for j in range(hsp):
                hyst_py[index][j] = ppy[2*hsp-2-j]-ppy[j]
                #print('PH',j,px[j],px[2*hsp-2-j], 'DY',ppy[2*hsp-2-j]-ppy[j],'Y',ppy[j],ppy[2*hsp-2-j])
            hyst_features.append(computeHystFeatures(hyst_px,hyst_py[index],0.4,25.))

    print("NB SMPLES",rindex,len(row_indexes))
    
    ##filter_df = tortuosity_df[tortuosity_df['ID'].isin(row_ids)]
    ##filter_df['TORTUOSITY'].plot.hist(bins=20)
    ##affiche(px,tortuosity_df,50,'ori')
    
    #afficheHyst(hyst_curves,tortuosity_df['TORTUOSITY'].values,10,"H")
    #afficheNP(hyst_px,hyst_py,tortuosity_df['TORTUOSITY'].values,10,"PH")
    #plotHystFeature(hyst_features,tortuosity_df['TORTUOSITY'].values,100)
    #return

    normalize(tortuosity_df,sp)
    #affiche(px,tortuosity_df,10,"norm")

    #filter_df = tortuosity_df[tortuosity_df['ID'].isin(row_ids)]
    #filter_df['TORTUOSITY'].plot.hist(bins=20)

    #X=filter_df.iloc[:,2:2+sp]
    #y=filter_df['TORTUOSITY'].values

    X=tortuosity_df.iloc[:,2:2+sp]
    y=tortuosity_df['TORTUOSITY'].values

    reducted_X,pca=computePCA(X.values,10)
    base_X=np.zeros([3,10],dtype=float)
    base_X[0][0] = 1.
    base_X[1][1] = 1.
    base_X[2][2] = 1.

    new_base_X=pca.inverse_transform(base_X)
    afficheBase(px,new_base_X)
    #return
    
    new_X=pca.inverse_transform(reducted_X)
    afficheNP(px,new_X,y,10,"Proj")
    
    ###########################################################################
    #
    # ANALYSE RECOUVREMENT DANS L ESPACE PC0, PC1, PC2
    #
    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(reducted_X, y, test_size=0.2, random_state=42)    
    plotTrainTestCover(X_train,X_test)
    
    #
    # ANALYSE RECOUVREMENT DANS L ESPACE F0, F1, F2
    #
    features_X=np.zeros([y.shape[0],3],dtype=float)
    index=0
    for feature in hyst_features:
        features_X[index][0]=feature[0]
        features_X[index][1]=feature[1]
        features_X[index][2]=feature[2]
        index=index+1
        
    X_train, X_test, y_train, y_test = train_test_split(features_X, y, test_size=0.2, random_state=42)  
    plotTrainTestCover(X_train,X_test)
    #return
    


    ###########################################################################
    #
    # BENCHMARK DES METHODES DE REGRESSION
    #
    from sklearn.svm import SVR
    from sklearn.ensemble.forest import RandomForestRegressor
    from sklearn.linear_model.ridge import Ridge
    from sklearn.linear_model import Lasso
    from sklearn.linear_model import ElasticNet
    #from sklearn.linear_model.stochastic_gradient import SGDRegressor
    #(SVR(gamma='scale', C=1.0, epsilon=0.2),"SVR2"),
    models = [(SVR(kernel='linear',degree=3),"SVR"),
              (RandomForestRegressor(max_depth=2, random_state=0,n_estimators=100),"RFR"),
              (Ridge(alpha=1.0),"RIDGE"),
              (Lasso(alpha=0.1),"LASSO"),
              (ElasticNet(alpha=1.0),"ElasiticNet")]
    #clf_sgd = SGDRegressor(max_iter=5)
    #
    # PCA DATA
    X_train, X_test, y_train, y_test = train_test_split(features_X, y, test_size=0.2, random_state=42)  
    for model in models:
        yy,err = compute_predict(model[0],model[1],X_train, X_test, y_train, y_test)
        plotRegressionModelResults(model[1],y_test,yy,err)


    ############################################################################
    #
    # XGBOOST TESTS
    #
    from XGBoostTools import OptimizeParams, computeXGBParam
    
    #
    # PCA DATA
    X_train, X_test, y_train, y_test = train_test_split(reducted_X, y, test_size=0.2, random_state=42) 
    params = computeXGBParam(X_train,y_train)
    yy_pred,yy_err = compute_xgb_predict("XGBoost-RedData",params,X_train, X_test, y_train, y_test)
    plotRegressionModelResults("XGBoost-RedData",y_test,yy_pred,yy_err) 
    
    #
    # Feature Data
    features_X=np.zeros([y.shape[0],3],dtype=float)
    index=0
    for feature in hyst_features:
        features_X[index][0]=feature[0]
        features_X[index][1]=feature[1]
        features_X[index][2]=feature[2]
        index=index+1
        
    X_train, X_test, y_train, y_test = train_test_split(features_X, y, test_size=0.2, random_state=42)   
    params = computeXGBParam(X_train,y_train)
    yy_pred,yy_err = compute_xgb_predict("XGBoost-FeatureData",params,X_train, X_test, y_train, y_test)
    plotRegressionModelResults("XGBoost-FeatureData",y_test,yy_pred,yy_err) 
    
    #
    # PCA + Feature Data
    reducted_nc=reducted_X.shape[1]
    reducted_features_X=np.zeros([y.shape[0],reducted_nc+3],dtype=float)
    index=0
    for feature in hyst_features:
        for j in range(reducted_nc):
            reducted_features_X[index][j] = reducted_X[index][j]
        reducted_features_X[index][reducted_nc]  =feature[0]
        reducted_features_X[index][reducted_nc+1]=feature[1]
        reducted_features_X[index][reducted_nc+2]=feature[2]
        index=index+1
        
    X_train, X_test, y_train, y_test = train_test_split(reducted_features_X, y, test_size=0.2, random_state=42) 
    params = computeXGBParam(X_train,y_train)
    yy_pred,yy_err = compute_xgb_predict("XGBoost-RedFeatureData",params,X_train, X_test, y_train, y_test)
    plotRegressionModelResults("XGBoost-RedFeatureData",y_test,yy_pred,yy_err) 

if __name__=="__main__":
    main()
    
#computeSVR(new_X,y)