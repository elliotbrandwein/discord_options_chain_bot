{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "import yahoo\n",
    "import pandas as pd"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "metadata": {},
   "outputs": [],
   "source": [
    "puts = pd.read_csv('outputs/puts_output.csv')\n",
    "calls = pd.read_csv('outputs/calls_output.csv')\n",
    "\n",
    "data = pd.concat([puts, calls])\n",
    "\n",
    "data['SD/MA'] = data['STD']/data['MA']\n",
    "data['% MA to adj'] = ((data['adjclose']/data['MA'])-1).apply(lambda x: abs(x))\n",
    "data['% ADJ to Strike'] = ((data['Strike']/data['adjclose'])-1).apply(lambda x: abs(x))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 31,
   "metadata": {},
   "outputs": [],
   "source": [
    "#calls first\n",
    "from sklearn.model_selection import train_test_split\n",
    "trainX, validX, trainY, validY = train_test_split(data[['SD/MA','% MA to adj','% ADJ to Strike']], data['Assigned'], test_size=0.33, random_state=42)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 32,
   "metadata": {},
   "outputs": [],
   "source": [
    "from sklearn.metrics import plot_confusion_matrix\n",
    "import matplotlib.pyplot as plt\n",
    "def plot_metric(clf, testX, testY, name):\n",
    "    \"\"\"\n",
    "    Small function to confusion matrix\n",
    "    \"\"\"\n",
    "    plt.style.use('ggplot')\n",
    "    plot_confusion_matrix(clf, testX, testY, normalize='true')\n",
    "    plt.title(f\"Confusion Matrix [{name}]\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 33,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Validation Accuracy of Random Forest Classifier is: 78.91%\n"
     ]
    }
   ],
   "source": [
    "from sklearn.ensemble import RandomForestClassifier\n",
    "rf_classifier = RandomForestClassifier()\n",
    "rf_classifier.fit(trainX, trainY)\n",
    "print(f\"Validation Accuracy of Random Forest Classifier is: {(rf_classifier.score(validX, validY))*100:.2f}%\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 34,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "image/png": "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\n",
      "text/plain": [
       "<Figure size 432x288 with 2 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "plot_metric(rf_classifier, validX, validY, \"Random Forest\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 35,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([0.26745698, 0.27920919, 0.45333383])"
      ]
     },
     "execution_count": 35,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "rf_classifier.feature_importances_"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 48,
   "metadata": {},
   "outputs": [],
   "source": [
    "import numpy as np\n",
    "sample_test = np.array([1.6021/15.2938, (16.94/15.2938)-1, (15/16.94)-1])\n",
    "#sample_test.reshape(1,-1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 49,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "1.0"
      ]
     },
     "execution_count": 49,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "rf_classifier.predict(sample_test.reshape(1,-1))[0]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 42,
   "metadata": {},
   "outputs": [],
   "source": [
    "from sklearn.linear_model import LogisticRegression\n",
    "log = LogisticRegression(random_state=42).fit(trainX, trainY)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 43,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[-0.40272519, -0.2207321 , -2.42391617]])"
      ]
     },
     "execution_count": 43,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "log.coef_"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 44,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0.7890625"
      ]
     },
     "execution_count": 44,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "log.score(validX, validY)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from joblib import dump\n",
    "dump(rf_classifier, 'models/rf_classifier.ai')"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "wheel_helper",
   "language": "python",
   "name": "wheel_helper"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
