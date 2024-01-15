import numpy as np
import torch.nn as nn
import torch
import click
import time


def pred_featNorm(features, mean, std):
  '''
  Normalize features by mean and standard deviation.
  Returns normalizedFeatures
  '''
  feats_norm = (features - mean) / (std + np.finfo(np.float32).eps)
  return feats_norm


def pred_featDenorm(features_norm, mean, std):
  '''
  Denormalize features by mean and standard deviation
  '''
  features = (features_norm * std) + mean
  return features


@click.command()
@click.argument('model_pt',  type=click.Path(exists=True))
@click.argument('predict_input_data_m', type=click.Path(exists=True))
@click.argument('inputs_mean_m', type=click.Path(exists=True))
@click.argument('inputs_std_m', type=click.Path(exists=True))
@click.argument('outputs_mean_m', type=click.Path(exists=True))
@click.argument('outputs_std_m', type=click.Path(exists=True))
@click.argument('predict_output_data_m', type=click.Path(exists=False))
def predict(model_pt='',
            predict_input_data_m='',
            inputs_mean_m='',
            inputs_std_m='',
            outputs_mean_m='',
            outputs_std_m='',
            predict_output_data_m=''):
  
  # start timer
  start_time = time.time()

  # load model
  model_path = model_pt

  # load predict input data
  predict_data_path = predict_input_data_m

  # load normalized mean and std data
  inputs_mean = torch.FloatTensor(np.loadtxt(inputs_mean_m))
  inputs_mean = inputs_mean.reshape(1,inputs_mean.shape[0])

  inputs_std = torch.FloatTensor(np.loadtxt(inputs_std_m))
  inputs_std = inputs_std.reshape(1,inputs_std.shape[0])

  outputs_mean = torch.FloatTensor(np.loadtxt(outputs_mean_m))
  outputs_mean = outputs_mean.reshape(1,outputs_mean.shape[0])
  
  outputs_std = torch.FloatTensor(np.loadtxt(outputs_std_m))
  outputs_std = outputs_std.reshape(1,outputs_std.shape[0])

  # load model
  model = torch.load(model_path)
  model.eval()

  # load predict input data
  predict_data = torch.FloatTensor(np.loadtxt(predict_data_path))

  # normalize predict input data
  predict_inputs_norm = pred_featNorm(predict_data, 
                                      inputs_mean, 
                                      inputs_std)

  # infer/predict output
  y_pred = model(predict_inputs_norm)

  # denormalize predict output
  y_pred_denorm = pred_featDenorm(y_pred,
                                  outputs_mean,
                                  outputs_std)

  # prep data to write output
  y_pred_denorm_np = y_pred_denorm.detach().numpy()

  # write_output
  np.savetxt(predict_output_data_m,y_pred_denorm_np)

  # end timer
  seconds = time.time() - start_time
  m, s = divmod(seconds, 60)
  h, m = divmod(m, 60)
  print 
  print( "--- infer_model - elapsed time: %d:%02d:%0.2f ---" % (h, m, s))
  print 


if __name__ == '__main__':
  predict()