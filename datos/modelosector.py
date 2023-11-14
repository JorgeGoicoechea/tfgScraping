import numpy as np
import pandas as pd
from fast_ml.model_development import train_valid_test_split
from transformers import Trainer, TrainingArguments, AutoConfig, AutoTokenizer, AutoModelForSequenceClassification
import torch
from torch import nn
from torch.nn.functional import softmax
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
import datasets

# Enable GPU accelerator if available
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#Prepare data from csv file
excel_file = '/home/jorge/tfg/datos/clasificacionsector.xlsx'
df = pd.read_excel(excel_file)
#print(df.head())
df_reviews = df.loc[:, ['Texto', 'Sector']].dropna()
#print(df_reviews.head())
#encodear los sectores, vamos a tranformar cada palabra en la taxonomia del sector en un numero para crear el modelo
le = LabelEncoder()
df_reviews['Sector'] = le.fit_transform(df_reviews['Sector'])
df_reviews.head()
#print(df_reviews.head(12))
#print (le.classes_)
# split the data into train, validation and test in the ratio of 80%, 10% and 10% respectively.
(train_texts, train_labels,val_texts, val_labels,
test_texts, test_labels) = train_valid_test_split(df_reviews, target = 'Sector', train_size=0.8, valid_size=0.1, test_size=0.1)
#Convert the review text from pandas series to list of sentences.
train_texts = train_texts['Texto'].to_list()
train_labels = train_labels.to_list()
val_texts = val_texts['Texto'].to_list()
val_labels = val_labels.to_list()
test_texts = test_texts['Texto'].to_list()
test_labels = test_labels.to_list()
#Create a DataLoader class for processing and loading of the data during training and inference phase.
class DataLoader(torch.utils.data.Dataset):
    def __init__(self, sentences=None, labels=None):
        self.sentences = sentences
        self.labels = labels
        self.tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
        
        if bool(sentences):
            self.encodings = self.tokenizer(self.sentences,
                                            truncation = True,
                                            padding = True)
        
    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        
        if self.labels == None:
            item['labels'] = None
        else:
            item['labels'] = torch.tensor(self.labels[idx])
        return item
    def __len__(self):
        return len(self.sentences)
    
    
    def encode(self, x):
        return self.tokenizer(x, return_tensors = 'pt').to(DEVICE)
    
train_dataset = DataLoader(train_texts, train_labels)
val_dataset = DataLoader(val_texts, val_labels)
test_dataset = DataLoader(test_texts, test_labels)
#print (train_dataset.__getitem__(0))
#Define Evaluation Metrics
"""El rendimiento del modelo debe evaluarse a intervalos durante la fase de entrenamiento. 
Para ello necesitamos una función de cálculo de métricas que acepte una tupla de (predicción, etiqueta) como argumento 
y devuelva un diccionario de métricas: {'métrica1':valor1,métrica2:valor2}."""

f1 = datasets.load_metric('f1')
accuracy = datasets.load_metric('accuracy')
precision = datasets.load_metric('precision')
recall = datasets.load_metric('recall')
def compute_metrics(eval_pred):
    metrics_dict = {}
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    
    metrics_dict.update(f1.compute(predictions = predictions, references = labels, average = 'macro'))
    metrics_dict.update(accuracy.compute(predictions = predictions, references = labels))
    metrics_dict.update(precision.compute(predictions = predictions, references = labels, average = 'macro'))
    metrics_dict.update(recall.compute(predictions = predictions, references = labels, average = 'macro'))
    return metrics_dict

#Training
#configure instantiate a distilbert-base-uncased model from pretrained checkpoint.
id2label = {idx:label for idx, label in enumerate(le.classes_)}
label2id = {label:idx for idx, label in enumerate(le.classes_)}
config = AutoConfig.from_pretrained('distilbert-base-uncased',
                                    num_labels = 4,
                                    id2label = id2label,
                                    label2id = label2id)
model = AutoModelForSequenceClassification.from_config(config)
#print(config)
#print(model)
#Define the training arguments
training_args = TrainingArguments(
    output_dir='/home/jorge/tfg/datos/resultadosmodelo',
    num_train_epochs=10,
    per_device_train_batch_size=64,
    per_device_eval_batch_size=64,
    warmup_steps=500,
    weight_decay=0.05,
    report_to='none',
    evaluation_strategy='steps',
    logging_dir='home/jorge/tfg/datos/',
    logging_steps=50)
#Instantiate the Trainer.
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics)

trainer.train()
