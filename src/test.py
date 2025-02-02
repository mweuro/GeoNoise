import torch
import torch.nn as nn
import torch.optim as optim
import json
from tqdm import tqdm
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from src.model import *
import json
import torchvision.transforms as transforms
from src.plots import plot_metrics



def evaluate_model(model, dataloader, criterion, device):
    model.eval()
    total_loss = 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for inputs, labels in tqdm(dataloader, desc="Testing", leave=False):
            inputs, labels = inputs.float().to(device), labels.to(device)

            # Forward
            outputs = model(inputs)
            loss = criterion(outputs, labels)

            total_loss += loss.item()
            all_preds.extend(torch.argmax(outputs, dim=1).cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    accuracy = accuracy_score(all_labels, all_preds)
    
    return total_loss / len(dataloader), accuracy



def load_data(data):
    transform = transforms.Compose([
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
    ])
    features_list, labels_list = get_data(data)
    train_loader, val_loader, test_loader = create_dataloaders(features_list, labels_list, transform, 32)
    
    return train_loader, val_loader, test_loader



def main():
    data = torch.load("data_to_train/tensors.pt")
    _, _, test_loader = load_data(data)
    
    model = CNNClassifier(num_classes = 4)
    model.load_state_dict(torch.load('model/best_model.pth'))
    criterion = nn.CrossEntropyLoss()


    test_loss, test_accuracy = evaluate_model(model, test_loader, criterion, "cpu")
    results = {"test loss": test_loss, "test accuracy": test_accuracy}
    
    with open('model/test/results.json', 'w') as f:
        json.dump(results, f, indent = 4)
    
    return




if __name__ == "__main__":
    main()