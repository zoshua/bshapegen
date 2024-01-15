import os
import json
import torch
import click
import time
import numpy as np
import torch.nn as nn


def featNorm(features):
  '''Normalize features by mean and standard deviation.
  Returns tuple (normalizedFeatures, mean, standardDeviation).
  '''
  mean = np.mean(features, axis=0)
  std = np.std(features - mean, axis=0)
  feats_norm = (features - mean) / (std + np.finfo(np.float32).eps)
  return (feats_norm, mean, std)


def featDenorm(features_norm, mean, std):
  '''Denormalize features by mean and standard deviation
  '''
  features = (features_norm * std) + mean
  return features


def fit(model,
        inputs,
        outputs,
        loss_func,
        optimizer,
        epochs=10,
        validation_split=None):
  #
  if validation_split != None:
    validation = True
    val_split_id = int(len(inputs)*(1-validation_split))
    val_inputs = inputs[:val_split_id]
    val_outputs = outputs[:val_split_id]
  else:
    validation = False
    val_split_id = len(inputs)

  train_inputs = inputs[val_split_id:]
  train_outputs = outputs[val_split_id:]
      
  train_loss_h = []
  val_loss_h = []
  
  for epoch in range(1,epochs+1): # count epochs starting with 1
    optimizer.zero_grad()
    # shuffle samples at every epoch
    shuffle_ids = list(range(val_split_id))
    np.random.shuffle(shuffle_ids)
    # feed-forward and backpropagate
    pred = model(inputs[shuffle_ids])
    #
    loss = loss_func(pred, outputs[shuffle_ids])
    train_loss_h.append(loss.item())
    loss.backward()
    optimizer.step()
      
    if validation:
      with torch.no_grad(): # validation should not mess with weights
        val_pred = model(inputs[:val_split_id])
        val_loss = loss_func(val_pred, outputs[:val_split_id])

        val_loss_h.append(loss.item())
      print ("[Epoch %d/%d] [loss: %f] [validation: %f]"
             % (epoch, epochs, loss.item(), val_loss.item()))
    
    else:
      print ("[Epoch %d/%d] [loss: %f] "
             % (epoch, epochs, loss.item()))

  return train_loss_h, val_loss_h


@click.command()
@click.argument('model_input_m',  type=click.Path(exists=True))
@click.argument('model_output_m', type=click.Path(exists=True))
@click.option('--neuron_num', default=512, help='512,1024,etc..')
@click.option('--learning_rate', default=0.001, help='0.001')
@click.option('--epochs', default=150, help='150')
@click.option('--validation_split', default=0.3, help='0.3 (30%)')
@click.argument('model_pt', type=click.Path(exists=False))
@click.argument('inputs_mean_m', type=click.Path(exists=False))
@click.argument('inputs_std_m', type=click.Path(exists=False))
@click.argument('outputs_mean_m', type=click.Path(exists=False))
@click.argument('outputs_std_m', type=click.Path(exists=False))
def make_model(model_input_m='',
               model_output_m='',
               neuron_num=512,
               learning_rate=0.001,
               epochs=150,
               validation_split=0.3,
               model_pt='',
               inputs_mean_m='',
               inputs_std_m='',
               outputs_mean_m='',
               outputs_std_m=''):
  
  # start timer
  start_time = time.time()

  # quick save of make_model params to json
  params = {'model_input_m':model_input_m,
            'model_output_m':model_output_m,
            'neuron_num':neuron_num,
            'learning_rate':learning_rate,
            'epochs':epochs,
            'validation_split':validation_split,
            'model_pt':model_pt,
            'inputs_mean_m':inputs_mean_m,
            'inputs_std_m':inputs_std_m,
            'outputs_mean_m':outputs_mean_m,
            'outputs_std_m':outputs_std_m}
  
  # get working dir from model_pt
  working_dir = os.path.dirname(model_pt)
  params_json = os.path.join(working_dir,'make_model_params.json')
  with open(params_json, 'w') as fp:
    json.dump(params, fp, indent=2)

  # load input/output training data
  inputs = np.loadtxt(model_input_m)
  outputs = np.loadtxt(model_output_m)

  print("inputs data shape: ",inputs.shape)
  print("outputs data shape:",outputs.shape)

  # normalize INPUTS
  inputNormalization = featNorm(inputs)
  inputs_norm = torch.FloatTensor(inputNormalization[0])

  inputs_mean = torch.FloatTensor(inputNormalization[1])
  inputs_mean = inputs_mean.reshape(1,inputs_mean.shape[0])

  inputs_std = torch.FloatTensor(inputNormalization[2])
  inputs_std = inputs_std.reshape(1,inputs_std.shape[0])

  # normalize OUTPUTS
  outputNormalization = featNorm(outputs)
  outputs_norm = torch.FloatTensor(outputNormalization[0])

  outputs_mean = torch.FloatTensor(outputNormalization[1])
  outputs_mean = outputs_mean.reshape(1,outputs_mean.shape[0])

  outputs_std = torch.FloatTensor(outputNormalization[2])
  outputs_std = outputs_std.reshape(1,outputs_std.shape[0])

  # init model
  model = nn.Sequential(nn.Linear(inputs.shape[1], neuron_num),
                        nn.Tanh(),
                        nn.Linear(neuron_num, neuron_num),
                        nn.Tanh(),
                        nn.Linear(neuron_num, outputs.shape[1]))

  # init optimizer
  optimizer = torch.optim.Adam(model.parameters(),
                               lr=learning_rate)

  # init loss function
  loss_func = nn.MSELoss()

  # run fit on model
  train_loss, val_loss = fit(model,
                             inputs_norm,
                             outputs_norm,
                             loss_func,
                             optimizer,
                             epochs=epochs,
                             validation_split=validation_split)

  # save model
  torch.save(model,model_pt)

  # save the normalized parameters (mean and std) for inference use
  np.savetxt(inputs_mean_m, inputs_mean)
  np.savetxt(inputs_std_m, inputs_std)
  np.savetxt(outputs_mean_m, outputs_mean)
  np.savetxt(outputs_std_m, outputs_std)

  # end timer
  seconds = time.time() - start_time
  m, s = divmod(seconds, 60)
  h, m = divmod(m, 60)
  print 
  print( "--- build_model - elapsed time: %d:%02d:%0.2f ---" % (h, m, s))
  print 

if __name__ == '__main__':
  make_model()