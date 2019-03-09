from net import DeepNet, AdvNet
from train import Train

class Job(object):
    def describe(self): return self.__class__.__name__
    def __init__(self, name, nfold, train_fold, epochs, hidden_Nlayer, hidden_Nnode, lr, momentum, output, activation, para_train={}):
        self.nfold = nfold
        self.train_fold = train_fold
        self.epochs = epochs
        self.hidden_Nlayer = hidden_Nlayer
        self.hidden_Nnode = hidden_Nnode
        self.lr = lr
        self.momentum = momentum
        self.activation = activation
        self.output = 'l{}n{}_lr{}mom{}_{}_k{}_e{}'.format(self.hidden_Nlayer, self.hidden_Nnode, self.lr, self.momentum, self.activation, self.nfold, self.epochs) if output is None else output
        self.name = self.output if name is None else name

        self.para_train = para_train
        para_train['base_directory'] = self.output

    def run(self):

        ''' An instance of Train for data handling '''
        self.trainer = Train(**self.para_train)
        self.trainer.split(nfold = self.nfold)

        ''' An instance of DeepNet for network construction and pass it to Train '''
        self.deepnet = DeepNet(name = self.name, build_dis = False, hidden_Nlayer = self.hidden_Nlayer, hidden_Nnode = self.hidden_Nnode, hidden_activation = self.activation)
        self.deepnet.build(input_dimension = self.trainer.shape, lr = self.lr, momentum = self.momentum)
        self.deepnet.plot(base_directory = self.output)
        self.trainer.getNetwork(self.deepnet.generator)
        
        ''' Run the training '''
        self.result = self.trainer.train(mode = 0, epochs = self.epochs, fold = self.train_fold)
        self.trainer.evaluate(self.result)
        self.trainer.plotLoss(self.result)
        self.trainer.plotResults()


class JobAdv(Job):
    def __init__(self, preTrain_epochs, hidden_auxNlayer, hidden_auxNnode, n_iteraction, lam, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.preTrain_epochs = preTrain_epochs
        self.hidden_auxNlayer = hidden_auxNlayer
        self.hidden_auxNnode = hidden_auxNnode
        self.n_iteraction = n_iteraction
        self.lam = lam
        self.output = '{}__E{}_L{}N{}_it{}_lam{}'.format(self.output, self.preTrain_epochs, self.hidden_auxNlayer, self.hidden_auxNnode, self.n_iteraction, self.lam)

    def run(self):

        ''' An instance of Train for data handling '''
        self.trainer = Train(**self.para_train)
        self.trainer.split(nfold = self.nfold)

        ''' An instance of AdvNet for network construction and pass it to Train '''
        self.advnet = AdvNet(name = self.name, build_dis = True, hidden_Nlayer = self.hidden_Nlayer, hidden_Nnode = self.hidden_Nnode,
            hidden_activation = self.activation, hidden_auxNlayer = self.hidden_auxNlayer, hidden_auxNnode = self.hidden_auxNnode)
        self.advnet.build(input_dimension = self.trainer.shape, lam = self.lam, lr = self.lr, momentum = self.momentum)
        self.advnet.plot(base_directory = self.output)
    
        ''' pre-training '''
        AdvNet.make_trainable(self.advnet.generator, True)
        AdvNet.make_trainable(self.advnet.discriminator, False)
        self.trainer.getNetwork(self.advnet.generator)
        self.result = self.trainer.train(mode = 0, epochs = self.preTrain_epochs, fold = self.train_fold)

        AdvNet.make_trainable(self.advnet.generator, False)
        AdvNet.make_trainable(self.advnet.discriminator, True)
        self.trainer.getNetwork(self.advnet.discriminator)
        self.result = self.trainer.train(mode = 1, epochs = self.preTrain_epochs, fold = self.train_fold)

        ''' Iterative training '''
        for i in range(self.n_iteraction):
            AdvNet.make_trainable(self.advnet.generator, True)
            AdvNet.make_trainable(self.advnet.discriminator, False)
            self.trainer.getNetwork(self.advnet.adversary)
            self.result = self.trainer.train(mode = 2, epochs = self.epochs, fold = self.train_fold)

            AdvNet.make_trainable(self.advnet.generator, False)
            AdvNet.make_trainable(self.advnet.discriminator, True)
            self.trainer.getNetwork(self.advnet.discriminator)
            self.result = self.trainer.train(mode = 1, epochs = self.epochs, fold = self.train_fold)

        self.trainer.evaluate(self.result)
        self.trainer.plotLoss(self.result)
        self.trainer.plotResults()

# job = Job(nfold = 3, train_fold = 0, epochs = 500, hidden_Nlayer = 20, hidden_Nnode = 100, lr = 0.01, momentum = 0.8)
# job.run()
# job = Job(nfold = 3, train_fold = 0, epochs = 500, hidden_Nlayer = 20, hidden_Nnode = 30, lr = 0.01, momentum = 0.8)
# job.run()
# job = Job(nfold = 3, train_fold = 0, epochs = 500, hidden_Nlayer = 20, hidden_Nnode = 100, lr = 0.01, momentum = 0.4)
# job.run()
# job = Job(nfold = 3, train_fold = 0, epochs = 500, hidden_Nlayer = 20, hidden_Nnode = 30, lr = 0.01, momentum = 0.4)
# job.run()
# job = Job(nfold = 3, train_fold = 0, epochs = 500, hidden_Nlayer = 20, hidden_Nnode = 50, lr = 0.02, momentum = 0.8)
# job.run()
# job = Job(nfold = 3, train_fold = 0, epochs = 500, hidden_Nlayer = 20, hidden_Nnode = 30, lr = 0.02, momentum = 0.8) # the best 75.2
# job.run()
# job = Job(nfold = 3, train_fold = 0, epochs = 500, hidden_Nlayer = 20, hidden_Nnode = 30, lr = 0.03, momentum = 0.8)
# job.run()
# job = Job(nfold = 3, train_fold = 0, epochs = 500, hidden_Nlayer = 10, hidden_Nnode = 30, lr = 0.03, momentum = 0.8)
# job.run()
# job = Job(nfold = 3, train_fold = 0, epochs = 500, hidden_Nlayer = 10, hidden_Nnode = 50, lr = 0.03, momentum = 0.8)
# job.run()
# job = Job(nfold = 3, train_fold = 0, epochs = 500, hidden_Nlayer = 10, hidden_Nnode = 100, lr = 0.03, momentum = 0.8) # the best 76.7
# job.run()
# job = Job(nfold = 3, train_fold = 0, epochs = 500, hidden_Nlayer = 10, hidden_Nnode = 150, lr = 0.03, momentum = 0.8)
# job.run()
# job = Job(nfold = 3, train_fold = 0, epochs = 500, hidden_Nlayer = 5, hidden_Nnode = 30, lr = 0.02, momentum = 0.8)
# job.run()
# job = Job(nfold = 3, train_fold = 0, epochs = 500, hidden_Nlayer = 5, hidden_Nnode = 50, lr = 0.02, momentum = 0.8)
# job.run()
# job = Job(nfold = 3, train_fold = 0, epochs = 500, hidden_Nlayer = 5, hidden_Nnode = 100, lr = 0.02, momentum = 0.8)
# job.run()
# job = Job(nfold = 3, train_fold = 0, epochs = 500, hidden_Nlayer = 5, hidden_Nnode = 30, lr = 0.03, momentum = 0.8)
# job.run()
# job = Job(nfold = 3, train_fold = 0, epochs = 500, hidden_Nlayer = 5, hidden_Nnode = 50, lr = 0.03, momentum = 0.8)
# job.run()
# job = Job(nfold = 3, train_fold = 0, epochs = 500, hidden_Nlayer = 5, hidden_Nnode = 100, lr = 0.03, momentum = 0.8)
# job.run()


para_train_sim = {'name': '2j2b',
    'signal_h5': '/Users/zhangrui/Work/Code/ML/ANN/h5files/tW_DR_2j2b.h5',
    'signal_name': 'tW_DR',
    'signal_tree': 'wt_DR_nominal',
    'backgd_h5': '/Users/zhangrui/Work/Code/ML/ANN/h5files/ttbar_2j2b.h5',
    'backgd_name': 'ttbar',
    'backgd_tree': 'tt_nominal',
    'weight_name': 'weight_nominal',
    'variables': ['mass_lep1jet2', 'mass_lep1jet1', 'deltaR_lep1_jet1', 'mass_lep2jet1', 'pTsys_lep1lep2met', 'pT_jet2', 'mass_lep2jet2'],
    }

para_net_sim = {
    'name': 'simple',
    'nfold': 3,
    'train_fold': 0,
    'epochs': 500,
    'hidden_Nlayer': 10,
    'hidden_Nnode': 100,
    'lr': 0.03,
    'momentum': 0.8,
    'output': None,
    'activation': 'elu',
    }

for hidden_Nlayer in [10, 20, 5]:
    for hidden_Nnode in [30, 50, 100]:
        for lr in [0.03, 0.05]:
            for activation in ['elu', 'relu']:
                para_net_sim['hidden_Nlayer'], para_net_sim['hidden_Nnode'], para_net_sim['lr'], para_net_sim['activation'] = hidden_Nlayer, hidden_Nnode, lr, activation
                job = Job(**para_net_sim, para_train = para_train_sim)
                job.run()

# para_train_Adv = {**para_train_sim,
#     'name': 'NP',
#     'no_syssig': False,
#     'syssig_h5': '/Users/zhangrui/Work/Code/ML/ANN/h5files/tW_DS_2j2b.h5',
#     'syssig_name': 'tW_DS',
#     'syssig_tree': 'wt_DS',
#     }

# para_net_Adv = {**para_net_sim,
#     'name': 'ANN',
#     'epochs': 2,
#     'hidden_auxNlayer': 2,
#     'hidden_auxNnode': 5,
#     'preTrain_epochs': 20,
#     'n_iteraction': 500,
#     'lam': 10,
# }
# job = JobAdv(**para_net_Adv, para_train = para_train_Adv)
# job.run()