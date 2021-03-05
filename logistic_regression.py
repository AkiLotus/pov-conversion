import numpy as np
import scipy.special

# sigmoid = lambda x: 1.0 / (1.0 + np.exp(-x))
sigmoid = lambda x: scipy.special.expit(x)
softmax = lambda x: scipy.special.softmax(x, axis=1)
__default_seed__ = 170299
__epsilon__ = 10 ** -6

def relative_error(x, y):
	return np.abs(x - y) / np.abs(x)

def absolute_error(x, y):
	return np.abs(x - y)

def cost_function(expected, reality):
	# it's a bernoulli thing
	return -expected * np.log(reality + __epsilon__) - (1 - expected) * np.log(1 - reality - __epsilon__)

def cost_function_multinomial(expected, reality):
	# still the same cost function but generalized
	return -np.sum(np.matmul(expected, np.transpose(np.log(reality + __epsilon__))))

def evaluate_binary(output_vector, true_vector):
	assert(len(np.shape(output_vector)) == 2)
	assert(len(np.shape(true_vector)) == 2)
	assert(min(output_vector) >= 0 and max(output_vector) <= 1)
	assert(min(true_vector) >= 0 and max(true_vector) <= 1)
	assert(len(output_vector) == len(true_vector))

	tp, tn, fp, fn = 0, 0, 0, 0
	for index in range(len(output_vector)):
		if output_vector[index] == 1:
			if true_vector[index] == 1: tp += 1
			if true_vector[index] == 0: fp += 1
		if output_vector[index] == 0:
			if true_vector[index] == 0: tn += 1
			if true_vector[index] == 1: fn += 1
	
	# print(tp, fp, fn, tn)

	accuracy = (tp + tn) / (tp + tn + fp + fn)
	precision = tp / (tp + fp)
	recall = tp / (tp + fn)

	return accuracy, precision, recall

def evaluate_multinomial(output_vector, true_vector, label_names):
	# microaverage by default
	assert(len(np.shape(output_vector)) == 2)
	assert(len(np.shape(true_vector)) == 2)
	assert(len(output_vector) == len(true_vector))

	# if label_names have only two value, use binary
	if len(label_names) == 2:
		output_vector = np.array([[(0 if x == label_names[0] else 1) for x in elem] for elem in output_vector])
		true_vector = np.array([[(0 if x == label_names[0] else 1) for x in elem] for elem in true_vector])
		acc, pre, rec = evaluate_binary(output_vector, true_vector)
		return acc, pre, rec

	tp, tn, fp, fn = 0, 0, 0, 0
	true, false = 0, 0
	for label in label_names:
		for index in range(len(output_vector)):
			if output_vector[index] == label:
				if true_vector[index] == label: tp += 1
				if true_vector[index] != label: fp += 1
			if output_vector[index] != label:
				if true_vector[index] != label: tn += 1
				if true_vector[index] == label: fn += 1
			if output_vector[index] == true_vector[index]: true += 1
			else: false += 1
		
		print('label {} / {} {} {} {} {} {}', label, tp, fp, fn, tn)
	
	print(true / len(output_vector), false / len(output_vector), tp, fp, fn, tn)

	accuracy = true / (true + false)
	precision = tp / (tp + fp)
	recall = tp / (tp + fn)

	return accuracy, precision, recall

class BinaryLogisticRegressionClassifier:
	def __init__(self, learning_rate = 1e-3, regularization_lambda = 0.4, seed=__default_seed__):
		self.learning_rate = learning_rate
		self.regularization_lambda = regularization_lambda
		self.weight_vector = None
		self.bias = 0
		self._seed = seed
		np.random.seed(seed)
	
	def __total_cost(self, feature_matrix, output_vector):
		assert(self.weight_vector is not None)
		assert(len(np.shape(self.weight_vector)) == 2)
		assert(len(np.shape(output_vector)) == 2)
		assert(min(output_vector) >= 0 and max(output_vector) <= 1)

		predicted = self.predict(feature_matrix, rounded=False)
		assert(len(output_vector) == len(predicted))
		cost = 0

		for index in range(len(predicted)):
			cost += cost_function(output_vector[index][0], predicted[index][0])

		return cost

	
	def fit(self, feature_matrix, output_vector, iterations=100, regularizing_metric='L2'):
		assert(len(np.shape(feature_matrix)) == 2)
		assert(len(np.shape(output_vector)) == 2)
		assert(np.shape(feature_matrix)[0] == np.shape(output_vector)[0])
		assert(min(output_vector) >= 0 and max(output_vector) <= 1)

		feature_matrix = np.array(feature_matrix)

		if self.weight_vector is None:
			self.weight_vector = np.random.rand(np.shape(feature_matrix)[1], 1)
			self.bias = np.random.random()
		m = np.shape(feature_matrix)[0]
		# print('initial weights:', self.weight_vector, self.bias)
		for iter in range(iterations):
			# print('matmul = ', np.matmul(np.transpose(feature_matrix), (self.predict(feature_matrix, rounded=False) - output_vector)))
			# print(np.concatenate(self.predict(feature_matrix, rounded=False))[:10])
			# print(np.concatenate(output_vector)[:10])
			# print(np.concatenate(self.predict(feature_matrix, rounded=False) - output_vector)[:10])
			prediction = self.predict(feature_matrix, rounded=False)
			weight_vector_gradient = np.matmul(feature_matrix.T, (prediction - output_vector))
			bias_gradient = np.sum(prediction - output_vector)

			if regularizing_metric == 'L2':
				weight_vector_gradient = weight_vector_gradient + self.learning_rate * self.regularization_lambda * self.weight_vector

			self.weight_vector = self.weight_vector - self.learning_rate * weight_vector_gradient
			self.bias = self.bias - self.learning_rate * bias_gradient
			# print('weight change:', weight_vector_gradient * self.learning_rate)
			# print('bias change:', bias_gradient * self.learning_rate)
			print('iteration #{}... cost = {}'.format(iter+1, self.__total_cost(feature_matrix, output_vector)))

	def predict(self, feature_matrix, rounded=True):
		assert(len(np.shape(feature_matrix)) == 2)
		assert(self.weight_vector is not None)
		assert(len(np.shape(self.weight_vector)) == 2)
		assert(np.shape(feature_matrix)[1] == np.shape(self.weight_vector)[0])

		output_vector = sigmoid(np.matmul(feature_matrix, self.weight_vector) + self.bias)
		if rounded: output_vector = np.round(output_vector)

		return output_vector
	
	def k_fold(self, feature_matrix, output_vector, k=10, regularizing_metric=None):
		assert(len(np.shape(feature_matrix)) == 2)
		assert(len(np.shape(output_vector)) == 2)
		assert(np.shape(feature_matrix)[0] == np.shape(output_vector)[0])
		assert(min(output_vector) >= 0 and max(output_vector) <= 1)

		n = np.shape(feature_matrix)[0]
		predicted_vector = None

		for iteration in range(k):
			train_set = np.concatenate((feature_matrix[:(n*iteration//k), :], feature_matrix[(n*(iteration+1)//k):, :]))
			test_set = feature_matrix[(n*iteration//k):(n*(iteration+1)//k):, :]

			train_res = np.concatenate((output_vector[:(n*iteration//k), :], output_vector[(n*(iteration+1)//k):, :]))

			self.fit(train_set, train_res, regularizing_metric=regularizing_metric)

			if predicted_vector is None:
				predicted_vector = self.predict(test_set)
			else: predicted_vector = np.concatenate((predicted_vector, self.predict(test_set)))
		
		accuracy, precision, recall = evaluate_binary(predicted_vector, output_vector)
		return accuracy, precision, recall



class MultinomialLogisticRegressionClassifier:
	def __init__(self, label_names = None, learning_rate = 1e-3, regularization_lambda = 1.0, absolute_tolerance = 1e-4, seed=__default_seed__):
		self.learning_rate = learning_rate
		self.regularization_lambda = regularization_lambda
		self.absolute_tolerance = absolute_tolerance
		self.weight_vector = None
		self.bias = None
		self._seed = seed
		np.random.seed(seed)

		self.label_names = label_names
		self.preset_labels = False if label_names is None else True
	
	def __total_cost(self, feature_matrix, output_matrix):
		assert(self.weight_vector is not None)
		assert(len(np.shape(self.weight_vector)) == 2)
		assert(len(np.shape(output_matrix)) == 2)

		predicted = self.predict(feature_matrix, rounded=False, displayed=False)
		assert(len(output_matrix) == len(predicted))
		cost = 0

		for index in range(len(predicted)):
			cost += cost_function_multinomial(output_matrix[index], predicted[index])

		return cost

	
	def fit(self, feature_matrix, output_vector, iterations=100, regularizing_metric='L2', return_cost=False):
		assert(len(np.shape(feature_matrix)) == 2)
		assert(len(np.shape(output_vector)) == 2)
		assert(np.shape(feature_matrix)[0] == np.shape(output_vector)[0])

		cost_logs = []

		if not self.preset_labels:
			temporal_set = set(output_vector.flatten().tolist())
			self.label_names = list(temporal_set)
		
		feature_matrix = np.array(feature_matrix)
		output_vector = np.array([self.label_names.index(name) for name in output_vector])
		output_matrix = np.zeros((np.shape(output_vector)[0], len(self.label_names)))
		for row_id in range(0, np.shape(output_matrix)[0]):
			output_matrix[row_id][output_vector[row_id]] = 1

		if self.weight_vector is None:
			self.weight_vector = (np.random.rand(np.shape(feature_matrix)[1], len(self.label_names)) - 0.5) * 1
			self.bias = (np.random.rand(len(self.label_names),) - 0.5) * 1
		m = np.shape(feature_matrix)[0]

		# print(self.weight_vector)
		# print(self.bias)
		current_cost = self.__total_cost(feature_matrix, output_matrix) / m
		print('iteration #0... cost = {}'.format(current_cost))
		if return_cost: cost_logs.append((current_cost, __epsilon__))

		last_cost = current_cost
		below_tolerance = False

		# print('initial weights:', self.weight_vector, self.bias)
		for iter in range(iterations):
			prediction = self.predict(feature_matrix, rounded=False)
			weight_vector_gradient = np.matmul(feature_matrix.T, (prediction - output_matrix))
			bias_gradient = np.sum(prediction - output_matrix, axis=0)

			if regularizing_metric == 'L2':
				weight_vector_gradient = weight_vector_gradient + self.regularization_lambda / m * self.weight_vector

			self.weight_vector = self.weight_vector - self.learning_rate * weight_vector_gradient
			self.bias = self.bias - self.learning_rate * bias_gradient
			# print('weight change:', weight_vector_gradient * self.learning_rate)
			# print('bias change:', bias_gradient * self.learning_rate)
			current_cost = self.__total_cost(feature_matrix, output_matrix) / m
			print('iteration #{}... cost = {}'.format(iter+1, current_cost))
			if return_cost: cost_logs.append((current_cost, iter+1))
			# if ((iter+1) % 100 == 0): print('iteration #{}...'.format(iter+1))
			# print('iteration #{}: {}, {}'.format(iter+1, self.weight_vector, self.bias))

			if absolute_error(last_cost, current_cost) < self.absolute_tolerance:
				if below_tolerance: break
				else: below_tolerance = True
			last_cost = current_cost
		
		if return_cost: return cost_logs

	def predict(self, feature_matrix, rounded=True, displayed=True):
		assert(len(np.shape(feature_matrix)) == 2)
		assert(self.weight_vector is not None)
		assert(len(np.shape(self.weight_vector)) == 2)
		assert(np.shape(feature_matrix)[1] == np.shape(self.weight_vector)[0])

		predicted_matrix = softmax(np.matmul(feature_matrix, self.weight_vector) + self.bias)

		if rounded:
			max_arguments = np.argmax(predicted_matrix, axis=1)
			if displayed:
				return np.array([[self.label_names[max_arg]] for max_arg in max_arguments])
			else:
				output_matrix = np.zeros(np.shape(predicted_matrix))
				for row_id in range(0, np.shape(output_matrix)[0]):
					output_matrix[row_id][max_arguments[row_id]] = 1
				return output_matrix
		return predicted_matrix
	
	def k_fold(self, feature_matrix, output_vector, k=10, regularizing_metric=None):
		assert(len(np.shape(feature_matrix)) == 2)
		assert(len(np.shape(output_vector)) == 2)
		assert(np.shape(feature_matrix)[0] == np.shape(output_vector)[0])

		n = np.shape(feature_matrix)[0]
		predicted_vector = None

		for iteration in range(k):
			train_set = np.concatenate((feature_matrix[:(n*iteration//k), :], feature_matrix[(n*(iteration+1)//k):, :]))
			test_set = feature_matrix[(n*iteration//k):(n*(iteration+1)//k):, :]

			train_res = np.concatenate((output_vector[:(n*iteration//k), :], output_vector[(n*(iteration+1)//k):, :]))

			print('batch', iteration+1, '...')

			self.fit(train_set, train_res, regularizing_metric=regularizing_metric)

			if predicted_vector is None:
				predicted_vector = self.predict(test_set)
			else: predicted_vector = np.concatenate((predicted_vector, self.predict(test_set)), axis=0)
		
		accuracy, precision, recall = evaluate_multinomial(predicted_vector, output_vector, self.label_names)
		return accuracy, precision, recall
