import torch
from torch import nn, optim

from TSB_AD.models.LSTMAD import LSTMAD
from TSB_AD.utils.torch_utility import EarlyStoppingTorch, get_gpu


class GRUModel(nn.Module):
    def __init__(self, window_size, feats, hidden_dim, pred_len, num_layers, batch_size, device):
        super().__init__()
        self.pred_len = pred_len
        self.batch_size = batch_size
        self.feats = feats
        self.device = device

        self.gru_encoder = nn.GRU(input_size=feats, hidden_size=hidden_dim, num_layers=num_layers, batch_first=True)
        self.gru_decoder = nn.GRU(input_size=feats, hidden_size=hidden_dim, num_layers=num_layers, batch_first=True)

        self.relu = nn.GELU()
        self.fc = nn.Linear(hidden_dim, feats)

    def forward(self, src):
        _, decoder_hidden = self.gru_encoder(src)
        cur_batch = src.shape[0]

        decoder_input = torch.zeros(cur_batch, 1, self.feats).to(self.device)
        outputs = torch.zeros(self.pred_len, cur_batch, self.feats).to(self.device)

        for t in range(self.pred_len):
            decoder_output, decoder_hidden = self.gru_decoder(decoder_input, decoder_hidden)
            decoder_output = self.relu(decoder_output)
            decoder_input = self.fc(decoder_output)
            outputs[t] = torch.squeeze(decoder_input, dim=-2)

        return outputs


class GRUAD(LSTMAD):
    def __init__(self, window_size=100, pred_len=1, batch_size=128, epochs=50, lr=0.0008,
                 feats=1, hidden_dim=20, num_layer=2, validation_size=0.2):
        self.y_hats = None
        self.cuda = True
        self.device = get_gpu(self.cuda)

        self.window_size = window_size
        self.pred_len = pred_len
        self.batch_size = batch_size
        self.epochs = epochs
        self.feats = feats
        self.hidden_dim = hidden_dim
        self.num_layer = num_layer
        self.lr = lr
        self.validation_size = validation_size

        self.model = GRUModel(window_size, feats, hidden_dim, pred_len, num_layer,
                              batch_size=batch_size, device=self.device).to(self.device)

        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.scheduler = optim.lr_scheduler.StepLR(self.optimizer, step_size=5, gamma=0.75)
        self.loss = nn.MSELoss()
        self.save_path = None
        self.early_stopping = EarlyStoppingTorch(save_path=self.save_path, patience=3)

        self.mu = None
        self.sigma = None
        self.eps = 1e-10
