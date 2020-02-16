import torch
idx = torch.Tensor([[0,3],[4,5]])
print(idx)
confidence = torch.Tensor([1,1,3,1,3,3])
iou = torch.Tensor([1,0.65, 0.7, 0.56])