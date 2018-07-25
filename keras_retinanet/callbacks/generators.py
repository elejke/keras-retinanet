import os
import shutil

import keras

class GeneratorStateCallback(keras.callbacks.Callback):
    
    def __init__(self, generator_restore_path):
        super().__init__()
        self.generator_restore_path = generator_restore_path
    
    def on_epoch_end(self, epoch, logs=None):
        
        if self.generator_restore_path is not None:
            groups_path = os.path.join(self.generator_restore_path, "groups.dump")
            group_index_path = os.path.join(self.generator_restore_path, "group_index.dump")
            if (os.path.exists(groups_path) and 
                os.path.exists(group_index_path)):
                shutil.copy(groups_path, 
                            os.path.join(self.generator_restore_path, "groups_at_checkpoint.dump"))
                shutil.copy(group_index_path, 
                            os.path.join(self.generator_restore_path, "group_index_at_checkpoint.dump"))