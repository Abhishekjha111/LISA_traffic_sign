'''
Global settings
'''
import tensorflow as tf


# DEFAULT_BOXES = ((x1_offset, y1_offset, x2_offset, y2_offset), (...), ...)
# Offset is relative to upper-left-corner and lower-right-corner of the feature map cell
DEFAULT_BOXES = ((-0.5, -0.5, 0.5, 0.5), (0.2, 0.2, -0.2, -0.2), (-0.8, -0.2, 0.8, 0.2), (-0.2, -0.8, 0.2, 0.8))
NUM_DEFAULT_BOXES = len(DEFAULT_BOXES)

# Constants 
NUM_CLASSES = 16  # 15 signs + 1 background class
NUM_CHANNELS = 1  # Use as grayscale = 1, RGB = 3
NUM_PRED_CONF = NUM_DEFAULT_BOXES * NUM_CLASSES  # number of class predictions per feature map cell
NUM_PRED_LOC  = NUM_DEFAULT_BOXES * 4  # number of localization regression predictions per feature map cell

# Bounding box parameters
IOU_THRESH = 0.5  # match ground-truth box to default boxes exceeding this IOU threshold, during data prep
NMS_IOU_THRESH = 0.2  # IOU threshold for non-max suppression

# Negatives-to-positives ratio used to filter training data
NEG_POS_RATIO = 5  # negative:positive = NEG_POS_RATIO:1

# Class confidence threshold to count as detection
CONF_THRESH = 0.9

# Model selection and dependent parameters
MODEL = 'AlexNet' 
if MODEL == 'AlexNet':
	 
	IMG_H, IMG_W = 260, 400
	FM_SIZES = [[31, 48], [15, 23], [8, 12], [4, 6]] # feature map sizes for SSD hooks via TensorBoard visualization (Height, Width)

else:
	raise NotImplementedError('Model not implemented')

# Model hyper-parameters
#OPT = tf.train.AdadeltaOptimizer()
OPT = tf.train.AdamOptimizer()
REG_SCALE = 1e-2  # L2 regularization strength
LOC_LOSS_WEIGHT = 1.  # weight of localization loss: loss = conf_loss + LOC_LOSS_WEIGHT * loc_loss

# Training process
RESUME = True # resume training from previously saved model?
NUM_EPOCH = 20
BATCH_SIZE = 16  # batch size for training (relatively small as it doesn't fits on GPU's memory if its bigger than 32)
TEST_SIZE = 0.20  # ratio of total training set to use as test set
SAVE_MODEL = True  # save trained model
MODEL_SAVE_PATH = './model.ckpt'  # where to save trained model
