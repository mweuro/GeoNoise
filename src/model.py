import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset, Dataset, random_split
import torchvision
from tqdm import tqdm
from sklearn.metrics import accuracy_score



class TransformedDataset(Dataset):
    def __init__(self, dataset, transform):
        self.dataset = dataset
        self.transform = transform

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        x, y = self.dataset[idx]
        x = self.transform(x)
        return x, y


def get_data(data: torch.tensor) -> tuple[list, list]:
    features_list = []
    labels_list = []

    for i in range(data.shape[0]):
        feature_map = data[i, :, :, 1:].permute(2, 0, 1)
        labels = data[i, :, :, 0]
        label = labels.mean()
        features_list.append(feature_map)
        labels_list.append(label)
    
    q25 = np.quantile(labels_list, 0.25)
    q50 = np.quantile(labels_list, 0.5)
    q75 = np.quantile(labels_list, 0.75)
    
    def quantize(value: float) -> int:
        if value <= q25:
            return 0
        elif value <= q50:
            return 1
        elif value <= q75:
            return 2
        else:
            return 3
    
    quantized_labels = [quantize(x) for x in labels_list]
    
    return features_list, quantized_labels



def create_dataset(features_list: list, labels_list: list) -> TensorDataset:
    labels = torch.tensor(labels_list)
    features = torch.stack(features_list)
    dataset = TensorDataset(features, labels)
    return dataset


def train_val_test_split(dataset: TensorDataset) -> tuple[TensorDataset, TensorDataset, TensorDataset]:
    return random_split(dataset, [0.7, 0.2, 0.1])


def create_dataloaders(features_list: list, 
                       labels_list: list,
                       transform: torchvision.transforms, 
                       batch_size: int = 32) -> tuple[DataLoader, DataLoader, DataLoader]:
    dataset = create_dataset(features_list, labels_list)
    train_dataset, val_dataset, test_dataset = train_val_test_split(dataset)
    train_dataset = TransformedDataset(train_dataset, transform)

    batch_size = 32
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    return train_loader, val_loader, test_loader
    


class CNNClassifier(nn.Module):
    def __init__(self, num_classes: int = 4) -> None:
        super(CNNClassifier, self).__init__()
        self.conv1 = nn.Conv2d(in_channels = 6, out_channels = 16, kernel_size = 3, padding = 1)
        self.bn1 = nn.BatchNorm2d(16)
        self.conv2 = nn.Conv2d(in_channels = 16, out_channels = 32, kernel_size = 3, padding = 1)
        self.bn2 = nn.BatchNorm2d(32)
        self.conv3 = nn.Conv2d(in_channels = 32, out_channels = 64, kernel_size = 3, padding = 1)
        self.bn3 = nn.BatchNorm2d(64)
        self.pool = nn.MaxPool2d(kernel_size = 2, stride = 2)
        self.fc1 = nn.Linear(64 * 3 * 3, 128)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(128, num_classes)
        
    def forward(self, x: torch.tensor) -> torch.tensor:
        x = self.pool(F.relu(self.bn1(self.conv1(x))))  # (16, 12, 12)
        x = self.pool(F.relu(self.bn2(self.conv2(x))))  # (32, 6, 6)
        x = self.pool(F.relu(self.bn3(self.conv3(x))))  # (64, 3, 3)
        x = x.view(-1, 64 * 3 * 3)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x



def _train(model: CNNClassifier, 
           dataloader: DataLoader,
           criterion: nn.CrossEntropyLoss, 
           optimizer: torch.optim, 
           device: str) -> tuple[float, float]:
    
    model.train()
    total_loss = 0
    all_preds = []
    all_labels = []

    for inputs, labels in tqdm(dataloader, desc = "Training", leave = False):
        inputs, labels = inputs.float().to(device), labels.to(device)

        # Forward
        outputs = model(inputs)
        loss = criterion(outputs, labels)

        # Backward
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        all_preds.extend(torch.argmax(outputs, dim = 1).cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

    accuracy = accuracy_score(all_labels, all_preds)

    return total_loss / len(dataloader), accuracy



def _validate(model: CNNClassifier, 
              dataloader: DataLoader,
              criterion: nn.CrossEntropyLoss,
              device: str) -> tuple[float, float]:
    
    model.eval()
    total_loss = 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for inputs, labels in tqdm(dataloader, desc = "Validation", leave = False):
            inputs, labels = inputs.float().to(device), labels.to(device)

            # Forward
            outputs = model(inputs)
            loss = criterion(outputs, labels)

            total_loss += loss.item()
            all_preds.extend(torch.argmax(outputs, dim = 1).cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    accuracy = accuracy_score(all_labels, all_preds)
    
    return total_loss / len(dataloader), accuracy




def train_model(model: CNNClassifier, 
                criterion: nn.CrossEntropyLoss, 
                optimizer: torch.optim, 
                num_epochs: int, 
                train_loader: DataLoader, 
                test_loader: DataLoader, 
                device: str, 
                patience: int = np.inf) -> tuple:
    
    train_losses = []
    val_losses = []
    train_accs = []
    val_accs = []
    best_acc = 0
    best_epoch = 0
    max_epoch = 0
    is_quit = 0
    
    for epoch in range(num_epochs):
        train_loss, train_acc = _train(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = _validate(model, test_loader, criterion, device)
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        train_accs.append(train_acc)
        val_accs.append(val_acc)
        max_epoch += 1
        
        if val_acc > best_acc:
            best_acc = val_acc
            best_epoch = epoch
            is_quit = 0
            torch.save(model.state_dict(), 'model/best_model.pth')
        else:
            is_quit += 1
            
        if (epoch + 1) % 5 == 0:
            print(f"Epoch {epoch + 1}/{num_epochs}")
            print(f"Train Loss: {train_loss:.4f},\
                    Train Accuracy: {train_acc:.4f}")
            print(f"Val Loss: {val_loss:.4f},\
                    Val Accuracy: {val_acc:.4f}")
            print("-" * 50)
        
        if is_quit > patience:
            break
    print(f"BEST EPOCH: {best_epoch:.2f}\
          BEST ACCURACY: {val_accs[best_epoch]:.2f}")
    
    return [*range(1, max_epoch + 1)], train_losses, val_losses, train_accs, val_accs, best_epoch