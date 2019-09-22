from sklearn import tree
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

# Training Data
X = [[181, 80, 44], [177, 70, 43], [160, 60, 38], 
     [154, 54, 37], [166, 65, 40], [190, 90, 47], 
     [175, 64, 39], [177, 70, 40], [159, 55, 37], 
     [171, 75, 42], [181, 85, 43]]

Y = ['male', 'male', 'female', 'female', 
  'male', 'male', 'female', 'female', 
  'female', 'male', 'male']

# Train the model
model = tree.DecisionTreeClassifier()
model.fit(X,Y)

# Export to ONNX
initial_type = [('float_input', FloatTensorType([1, 1]))]
onx = convert_sklearn(model, initial_types=initial_type)
with open("gender_classifier.onnx", "wb") as f:
	f.write(onx.SerializeToString())
