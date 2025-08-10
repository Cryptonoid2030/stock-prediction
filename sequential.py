import numpy as np

def discretize_prediction(pred):
    # Round note to integer MIDI note, clip durations if needed
    duration = pred[0]
    note = int(round(pred[1]))
    # Optional: clip note range
    note = np.clip(note, 0, 127)
    return np.array([duration, note])

def sequential_predict(model, initial_input, pred_steps=50):
    """
    model: trained keras model
    initial_input: np.array shape (window_size, features), e.g. (3, 2)
    pred_steps: how many steps to predict sequentially
    
    Returns:
      predictions: list of predicted [duration, note] pairs
    """
    input_seq = initial_input.copy()
    predictions = []
    
    for _ in range(pred_steps):
        # Add batch dimension
        pred = model.predict(input_seq[np.newaxis, ...])[0]
        
        # Discretize note and optionally clip duration
        pred_disc = discretize_prediction(pred)
        predictions.append(pred_disc)
        
        # Slide window: drop oldest, append predicted step
        input_seq = np.vstack([input_seq[1:], pred_disc])
    
    return np.array(predictions)
