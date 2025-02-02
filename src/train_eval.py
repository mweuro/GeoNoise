from src.model import *
import json
import torchvision.transforms as transforms
from src.plots import plot_metrics



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
    train_loader, val_loader, _ = load_data(data)
    
    model = CNNClassifier(num_classes = 4)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr = 0.001, weight_decay = 1e-4)
    n_epochs = 50
    _, train_losses, val_losses, train_accs, val_accs, best_epoch = train_model(model, \
                                                                                     criterion, \
                                                                                     optimizer, \
                                                                                     n_epochs, \
                                                                                     train_loader, \
                                                                                     val_loader, \
                                                                                     "cpu")
    results = {'best_loss': val_losses[best_epoch], 'best_acc': val_accs[best_epoch]}
    with open('model/val/best_results.json', 'w') as f:
        json.dump(results, f, indent=4)
    
    plot_metrics(train_losses, val_losses, train_accs, val_accs, 'model/val/metrics.png')
    print('Results saved to model/val/best_results.json')
    print('Plot saved to model/val/metrics.png')



if __name__ == "__main__":
    main()