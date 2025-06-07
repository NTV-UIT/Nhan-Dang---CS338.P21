"""Legacy code for backwards compatibility."""

import os
import pickle
import numpy as np
import tensorflow as tf
import dnnlib
import dnnlib.tflib as tflib

#----------------------------------------------------------------------------

def load_network_pkl(f, force_fp16=False):
    """Load legacy network pickle file."""
    data = _LegacyUnpickler(f).load()
    return convert_network_pkl(data, force_fp16)

def convert_network_pkl(data, force_fp16=False):
    """Convert legacy network pickle data."""
    # Convert to new format.
    if isinstance(data, tuple):
        net, const = data
        data = dict(G=net, G_ema=net, D=None, training_set_kwargs=dict())
        if const is not None:
            data['G'].mapping.const = tf.constant(const, name='const')
            data['G_ema'].mapping.const = tf.constant(const, name='const')

    # Add missing fields.
    if 'training_set_kwargs' not in data:
        data['training_set_kwargs'] = dict()
    if 'augment_kwargs' not in data:
        data['augment_kwargs'] = dict()
    if 'augment_p' not in data:
        data['augment_p'] = 0.0

    # Validate contents.
    assert isinstance(data, dict)
    assert all(key in data for key in ['G', 'G_ema', 'D', 'training_set_kwargs', 'augment_kwargs', 'augment_p'])
    assert all(isinstance(data[key], tf.keras.Model) for key in ['G', 'G_ema'])
    assert isinstance(data['training_set_kwargs'], dict)
    assert isinstance(data['augment_kwargs'], dict)
    assert isinstance(data['augment_p'], float)

    return data

#----------------------------------------------------------------------------

class _LegacyUnpickler(pickle.Unpickler):
    """Legacy unpickler for backwards compatibility."""
    def find_class(self, module, name):
        if module == 'dnnlib.tflib.network' and name == 'Network':
            return tf.keras.Model
        if module == 'dnnlib.tflib.optimizer' and name == 'Optimizer':
            return tf.keras.optimizers.Optimizer
        return super().find_class(module, name)

#---------------------------------------------------------------------------- 