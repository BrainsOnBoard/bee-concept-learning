%DMTS task
clc;
clear;
close all;

function y = logsig(x)
y = 1 ./ (1 + exp(-x));
end

%it is more difficult to learn DMTS than DNMTS.
%Inverting the representations changes the situation, but then the initial DIP in the fugure is not present. 

maxActivity=2;
minActivity=0.0; %in the first layer the min activity has to be 0 or low for this scheme to work; 
%This is because the connectivity from low stimulus to NoGO (and high stimulus to NoGo) is not
%learnend, as NoGo is not rewarded and there is no eligibility trace 
%and if there is some input to Go when NoGo is the correct choice , the NoGO activity cannot increase to surpass this; 
maxWeight=1;
minWeight=0.0;

lowAct=0.2;
highAct=0.4;

theta=lowAct*maxWeight*1.1; % High frequency detector

logsigCoeff=80; %controls steepness of logsig in the decisionmaking process ?
logsigOff=1.0; % changes the steepness if a decision Go takes too long (i.e. increases noise)

lrateExc=0.06;
rewardBaselineExc=0.66666;

lrateInh=0.03;%
rewardBaselineInh=0.66666; %reward baseline, anything below is considered "pubishment". 
%As reward is binary, effectively this gives grater learning rate for punsihment than reward, which may be explained for evolutionary reasons.
%This is required as there is a connection learned from the low frequency
%neurons to the GO stimulus that can only be decreased by strong synaptic
%changes in case of punishment
%to have the first "DiP" one needs to have rewardBaseline=0.9, so that a
%mistake reduces significantly the connection from LOW frequency neurons to
%go that at the beginning 
%there is a condition that mistakes take place with these parameters that
%can be calculated by finding when the probablility for the repeated
%stimulus to Go becomes smaller from the probability for the non-repeated
%stimulus to Go
%the condition is 5*W32(1,1)+2*W32(1,2)<7
%This is due to W32(2,1) and W32(2,2) being fixed to 1 and never learned as NOGO is non rewarded and there is no eligibility trace



changeFreq=4;  

trials=60;
trialsPerBlock=10; %10 trials per block, 1 block for transfer learning
bees=360;

% Stimulus is represented column-wise.
% the first element can be considered a context encoding (background) activity 
% the second element of the column represents stimulus 1
% the third element represents stimulus 2
% the fourth element represents transfer stimulus 1
% the fifth element represents transfer stimulus 2
% est stimulus representation has two values: lowAct, if stimulus in recent
% past has been only seen once or  highAct if stimulus has been only seen
% twice.
% The bee has to chose either the stimulus with high activity or low
% activity. The representation of the stululus depends only on the stumulus
% 
% Sequence
% Y - Y B - Stimulus 2 followed by a choice between 1 and 2 that can be
% placed either 1: left arem of the maze 2: right arm of the mase or vice
% versa.
% Y - B Y
% B - Y B - Stimulus 1 followed by a choice between 1 and 2
% B - B Y
% The assumtion is that when there are two choices, the bee sees choice one
% or choice 2 but not both at the same time, and it alternates between these two options.
%
% Stimulus is the input layer of the simulated network (X1). In the second layer (X2) there are two neurons 

trainStimulus=[  0.0     0.0       % background activity
                 0.0     0.0       % background activity
                 0.0     0.0       % stimulus 1
                 0.0     0.0       % stimulus 2     
                 0.0     0.0       % transfer stimulus 1
                 0.0     0.0       % transfer stimulus 2  
                 0.0     highAct   % train stimulus 1
                 highAct 0.0       % train stimulus 2
          ]; 



Stimulus=[0.0    0.0     0.0      0.0    % background activity
          0.0    0.0     0.0      0.0    % background activity
          lowAct 0.0     highAct  0.0    % stimulus 1
          0.0    highAct 0.0      lowAct % stimulus 2
          0.0    0.0     0.0      0.0    % transfer stimulus 1
          0.0    0.0     0.0      0.0    % transfer stimulus 2     
          0.0    0.0     0.0      0.0    % train stimulus 1
          0.0    0.0     0.0      0.0    % train stimulus 2  
          ]; 
      
transStimulus=[0.0    0.0     0.0      0.0    % background activity
               0.0    0.0     0.0      0.0
               0.0    0.0     0.0      0.0
               0.0    0.0     0.0      0.0
               lowAct 0.0     highAct  0.0
               0.0    highAct 0.0      lowAct
               0.0    0.0     0.0      0.0    % train stimulus 1
               0.0    0.0     0.0      0.0    % train stimulus 2  
               ]; 
          
           
X1=zeros(size(Stimulus,1),1); % Input layer. Elements: Contact, Stimulus 1, Stimulus 2, Transfer Stimulus 1, Transfer Stimulus 2
X2=zeros(1,1); % Frequency detectors. Fires only on non-repeated stimuli
X3=zeros(2,1); % Go, NoGo Neurons   

W21=maxWeight*1.0*ones(size(X2,1),size(Stimulus,1),bees); %weights from (input) layer 1 to layer 2
W31=maxWeight*0.5*ones(size(X3,1),size(Stimulus,1),bees);
W32=maxWeight*0.5*ones(size(X3,1),size(X2,1),bees);       %weights from layer 2 to (putput) layer 3   
    
% bias from pretrain
W32(1,:,:) = 0.35;

rewardedStimulus=ones(1,trials);% (same for all bees);

for k=1:trials %predecide the pattern presentation sequence
    if mod(k-1,2*changeFreq)<changeFreq
        rewardedStimulus(1,k)=2; %if I want to change this to 1, I need to initialize rewardedStimulus with 2's
    end
end

Reward=zeros(bees,trials);

transRewardedStimulus=ones(1,trialsPerBlock);% (same for all bees);

for k=1:trialsPerBlock %predecide the pattern presentation sequence in transfer learning
    if mod(k-1,2*changeFreq)<changeFreq
        transRewardedStimulus(1,k)=2;
    end
end

transReward=zeros(bees,trialsPerBlock);



%Delayed NOT match to sample

%patterns presented in the same order as Learning

notMatchToSampleReward=zeros(bees,trials);
transnotMatchToSampleReward=zeros(bees,trialsPerBlock);


% nmtsW21=maxWeight*0.5*ones(size(X2,1),size(Stimulus,1),bees); %weights from (input) layer 1 to layer 2
% nmtsW31=maxWeight*0.5*ones(size(X3,1),size(Stimulus,1),bees);
% nmtsW32=maxWeight*0.5*ones(size(X3,1),size(X2,1),bees);  

%{
for b=1:bees
    
    for k=1:trials
        
  
            S1=trainStimulus(:,1); %
            S2=trainStimulus(:,2);
     
        
        noexit=1;
        wait=0;
        
        while noexit
            seen=rand<0.5; %randomly focus on one of the stimulus.
            
            X1=S1*seen+S2*(1-seen);
           
            X2=W21(:,:,b)*X1;
            X2=X2.*(X2>theta);

            %Making sure activities are beween minActivity and maxActivity
            X2=X2.*(X2<maxActivity)+maxActivity*(X2>=maxActivity);
            X2=X2.*(X2>minActivity)+minActivity*(X2<=minActivity);

            
            X3=-W32(:,:,b)*X2+W31(:,:,b)*X1;
            
            %Making sure activities are beween minActivity and maxActivity
            X3=X3.*(X3<maxActivity)+maxActivity*(X3>=maxActivity);
            X3=X3.*(X3>minActivity)+minActivity*(X3<=minActivity);
%           
            %X3 is go, X2 is no Go
           
            diff=(X3(1,1)-X3(2,1)); % Neuron X3(1,1) is Go, X3(2,1) No go
            
            prob=logsig(diff*(logsigCoeff-wait/logsigOff)); %probability of chosing Go %probability of chosing Go
          
            choice=rand<prob;  
            
            if (choice==1) % Go was chosen, only then reward will be administered
                %Go neuron X3(1,1) wan the competition hence is set to
                %maxActivity, noGo Neuron X3(2,1) lost the competition and set to minActivity
                
                X3(1,1)=maxActivity;
                X3(2,1)=minActivity;
                
                reward=1; % reward if I made the right choice, i.e. chosen the pattern previosuly seen, i.e. lowest activity
                Reward(b,k)=reward;
                noexit=0;

                %Learning excitatory weights
                W31(1,:,b)=W31(1,:,b)+lrateExc*(reward-rewardBaselineExc)* X3(1,1)*X1';
                
                %Learning inhibitory weights
                W32(1,:,b)=W32(1,:,b)-lrateInh*(reward-rewardBaselineInh)* X3(1,1)*X2'; %minus sign in the calculation of X3
                    
                %weights have upper and lower bounds
                W32(:,:,b)=W32(:,:,b).*(W32(:,:,b)<maxWeight)+maxWeight*(W32(:,:,b)>=maxWeight);
                W32(:,:,b)=W32(:,:,b).*(W32(:,:,b)>minWeight)+minWeight*(W32(:,:,b)<=minWeight);
                
                W31(:,:,b)=W31(:,:,b).*(W31(:,:,b)<maxWeight)+maxWeight*(W31(:,:,b)>=maxWeight);
                W31(:,:,b)=W31(:,:,b).*(W31(:,:,b)>minWeight)+minWeight*(W31(:,:,b)<=minWeight);
                
            end
            wait=wait+1;
            
        end
        
    end     
end
%}


nmtsW21=W21; %weights from (input) layer 1 to layer 2
nmtsW31=W31;
nmtsW32=W32;  




for b=1:bees
    
    for k=1:trials
        
        if rewardedStimulus(1,k)==2 % 
            %stimulus 2 first followed by 1 and 2
            S1=Stimulus(:,1); %
            S2=Stimulus(:,2);
        else
            %stmulus 1 first followed by 1 and 2
            S1=Stimulus(:,3);
            S2=Stimulus(:,4);
        end
        
        noexit=1;
        wait=0;
        
        while noexit
            seen=rand<0.5; %randomly focus on one of the stimulus.
            
            X1=S1*seen+S2*(1-seen);
           
            X2=W21(:,:,b)*X1;
            X2=X2-theta;
            X2=X2.*(X2>0);

            %Making sure activities are beween minActivity and maxActivity
            X2=X2.*(X2<maxActivity)+maxActivity*(X2>=maxActivity);
            X2=X2.*(X2>minActivity)+minActivity*(X2<=minActivity);

            
            X3=-0.25*W32(:,:,b)*X2+W31(:,:,b)*X1;
            
            %Making sure activities are beween minActivity and maxActivity
            X3=X3.*(X3<maxActivity)+maxActivity*(X3>=maxActivity);
            X3=X3.*(X3>minActivity)+minActivity*(X3<=minActivity);
%           
            %X3 is go, X2 is no Go
           
            diff=(X3(1,1)-X3(2,1)); % Neuron X3(1,1) is Go, X3(2,1) No go

            
            prob=logsig(diff*(logsigCoeff-wait/logsigOff)); %probability of chosing Go %probability of chosing Go
          
            choice=rand<prob;  
            
            if (choice==1) % Go was chosen, only then reward will be administered
                %Go neuron X3(1,1) wan the competition hence is set to
                %maxActivity, noGo Neuron X3(2,1) lost the competition and set to minActivity
                
                X3(1,1)=1;
                X3(2,1)=0;
                
                reward=(max(X1)==lowAct); % reward if I made the right choice, i.e. chosen the pattern previosuly seen, i.e. lowest activity
                Reward(b,k)=reward;
                noexit=0;

                %Learning excitatory weights
                W31(1,:,b)=W31(1,:,b)+lrateExc*(reward-rewardBaselineExc)*(X3(1,1)>0)*(X1>0)';
                %W31(1,:,b)
                
                %Learning inhibitory weights
                W32(1,:,b)=W32(1,:,b)-lrateInh*(reward-rewardBaselineInh)*(X3(1,1)>0)*(X2>0)'; %minus sign in the calculation of X3
                %W32(1,:,b)
                %(X2>0)
                %lrateInh*(reward-rewardBaselineInh)*(X3(1,1)>0)*(X2>0)'
                    
                %weights have upper and lower bounds
                W32(:,:,b)=W32(:,:,b).*(W32(:,:,b)<maxWeight)+maxWeight*(W32(:,:,b)>=maxWeight);
                W32(:,:,b)=W32(:,:,b).*(W32(:,:,b)>minWeight)+minWeight*(W32(:,:,b)<=minWeight);
                
                W31(:,:,b)=W31(:,:,b).*(W31(:,:,b)<maxWeight)+maxWeight*(W31(:,:,b)>=maxWeight);
                W31(:,:,b)=W31(:,:,b).*(W31(:,:,b)>minWeight)+minWeight*(W31(:,:,b)<=minWeight);
                
            end
            wait=wait+1;
            
        end
        
    end     
end
 
    %Store weights after learning
    W31Learning=W31;
    W32Learning=W32;
  
    
    %Transfer learning test   

    
for b=1:bees   
     for k=1:trialsPerBlock
        
        if transRewardedStimulus(1,k)==2  
            %stimulus B first followed by A and B
            S1=transStimulus(:,1); 
            S2=transStimulus(:,2);
        else
            %stmulus A first followed by A and B
            S1=transStimulus(:,3);
            S2=transStimulus(:,4);
        end
        
        noexit=1;
        wait=0;
        
        
        while noexit
            seen=rand<0.5; %randomly focus on one of the stimulus.
            
            X1=S1*seen+S2*(1-seen);
            X2=W21(:,:,b)*X1;
            X2=X2-theta;
            X2=X2.*(X2>0);
            
            %Making sure activities are beween minActivity and maxActivity
            X2=X2.*(X2<maxActivity)+maxActivity*(X2>=maxActivity);
            X2=X2.*(X2>minActivity)+minActivity*(X2<=minActivity);
                    
            X3=-0.25*W32(:,:,b)*X2+W31(:,:,b)*X1;
            
            %Making sure activities are beween minActivity and maxActivity
            X3=X3.*(X3<maxActivity)+maxActivity*(X3>=maxActivity);
            X3=X3.*(X3>minActivity)+minActivity*(X3<=minActivity);
       
            %X3 is go, X2 is no Go
            
            diff=(X3(1,1)-X3(2,1)); % Neuron X3(1,1) is Go, X3(2,1) NoGo     
            prob=logsig(diff*(logsigCoeff-wait/logsigOff)); %probability of chosing Go %probability of chosing Go
            
            choice=rand<prob;
            
            if (choice==1) % Go was chosen, only then reward will be administered
                %Go neuron X3(1,1) wan the competition hence is set to
                %maxActivity, noGo Neuron X3(2,1) lost the competition and set to minActivity
                
                X3(1,1)=1;
                X3(2,1)=0;
                
                reward=(max(X1)==lowAct); % reward if I made the right choice, i.e. chosen the pattern previosuly seen, i.e. lowest activity
                transReward(b,k)=reward;
                noexit=0;
                
                
            end
            wait=wait+1;
            
        end
     
     end
     
end

W31TransferLearning=W31;
W32TransferLearning=W32;


%Delayed not match to sample

%display(mean(nmtsW32,3))    %check weight initialization

for b=1:bees

    for k=1:trials

        if rewardedStimulus(1,k)==2 %
            %stimulus 2 first followed by 1 and 2
            S1=Stimulus(:,1); %
            S2=Stimulus(:,2);
        else
            %stmulus 1 first followed by 1 and 2
            S1=Stimulus(:,3);
            S2=Stimulus(:,4);
        end

        noexit=1;
        wait=0;

        while noexit
            seen=rand<0.5; %randomly focus on one of the stimulus.

            X1=S1*seen+S2*(1-seen);
            X2=nmtsW21(:,:,b)*X1;
            X2=X2-theta;
            X2=X2.*(X2>0);

            %Making sure activities are beween minActivity and maxActivity
            X2=X2.*(X2<maxActivity)+maxActivity*(X2>=maxActivity);
            X2=X2.*(X2>minActivity)+minActivity*(X2<=minActivity);

            X3=-0.25*nmtsW32(:,:,b)*X2+nmtsW31(:,:,b)*X1;

            %Making sure activities are beween minActivity and maxActivity
            X3=X3.*(X3<maxActivity)+maxActivity*(X3>=maxActivity);

            %X3(2,1) += 0.05;

            %X3 is Go, X2 is no Go

            diff=(X3(1,1)-X3(2,1)); % Neuron X3(1,1) is Go, X3(2,1) No go
            
            prob=logsig(diff*(logsigCoeff-wait/logsigOff)); %probability of chosing Go
         
            choice=rand<prob;

            if (choice==1) % Go was chosen, only then reward will be administered
                %Go neuron X3(1,1) wan the competition hence is set to
                %maxActivity, noGo Neuron X3(2,1) lost the competition and set to minActivity

                X3(1,1)=maxActivity;
                X3(2,1)=minActivity;

                reward=(max(X1)==highAct); % reward if I made the right choice, i.e. chosen the pattern previosuly seen, i.e. highest activity
                notMatchToSampleReward(b,k)=reward;
                noexit=0;
                
                
                %Learning excitatory weights
                nmtsW31(1,:,b)=nmtsW31(1,:,b)+lrateExc*(reward-rewardBaselineExc)*X3(1,1)*X1';
                
                %Learning inhibitory weights
                nmtsW32(1,:,b)=nmtsW32(1,:,b)-lrateInh*(reward-rewardBaselineInh)*(X3(1,1)>0)*(X2>0)'; %minus sign in the calculation of X3
         

               
                %weights have upper and lower bounds
                nmtsW31(:,:,b)=nmtsW31(:,:,b).*(nmtsW31(:,:,b)<maxWeight)+maxWeight*(nmtsW31(:,:,b)>=maxWeight);
                nmtsW31(:,:,b)=nmtsW31(:,:,b).*(nmtsW31(:,:,b)>minWeight)+minWeight*(nmtsW31(:,:,b)<=minWeight);
                
                nmtsW32(:,:,b)=nmtsW32(:,:,b).*(nmtsW32(:,:,b)<maxWeight)+maxWeight*(nmtsW32(:,:,b)>=maxWeight);
                nmtsW32(:,:,b)=nmtsW32(:,:,b).*(nmtsW32(:,:,b)>minWeight)+minWeight*(nmtsW32(:,:,b)<=minWeight);
            end
            wait=wait+1;
            
        end
        
    end   
    
end


%% NMTS transfer
 for b=1:bees   
     for k=1:trialsPerBlock
        
        if transRewardedStimulus(1,k)==2  
            %stimulus B first followed by A and B
            S1=transStimulus(:,1); 
            S2=transStimulus(:,2);
        else
            %stmulus A first followed by A and B
            S1=transStimulus(:,3);
            S2=transStimulus(:,4);
        end
        
        noexit=1;
        wait=0;
        
        
        while noexit
            seen=rand<0.5; %randomly focus on one of the stimulus.
            
            X1=S1*seen+S2*(1-seen);
            X2=nmtsW21(:,:,b)*X1;
            X2=X2-theta;
            X2=X2.*(X2>0);
            
            %Making sure activities are beween minActivity and maxActivity
            X2=X2.*(X2<maxActivity)+maxActivity*(X2>=maxActivity);
            X2=X2.*(X2>minActivity)+minActivity*(X2<=minActivity);
                    
            X3=-0.25*nmtsW32(:,:,b)*X2+nmtsW31(:,:,b)*X1;
            
            %Making sure activities are beween minActivity and maxActivity
            X3=X3.*(X3<maxActivity)+maxActivity*(X3>=maxActivity);
            X3=X3.*(X3>minActivity)+minActivity*(X3<=minActivity);
       
            %X3 is go, X2 is no Go
            
            diff=(X3(1,1)-X3(2,1)); % Neuron X3(1,1) is Go, X3(2,1) NoGo     
            prob=logsig(diff*(logsigCoeff-wait/logsigOff)); %probability of chosing Go %probability of chosing Go
            
            choice=rand<prob;
            
            if (choice==1) % Go was chosen, only then reward will be administered
                %Go neuron X3(1,1) wan the competition hence is set to
                %maxActivity, noGo Neuron X3(2,1) lost the competition and set to minActivity
                
                X3(1,1)=1;
                X3(2,1)=0;
                
                reward=(max(X1)==highAct); % reward if I made the right choice, i.e. chosen the pattern previosuly seen, i.e. lowest activity
                transnotMatchToSampleReward(b,k)=reward;
                noexit=0;
                
     
            end
            wait=wait+1;
            
        end
     
     end
     
end


blocks=floor(trials/trialsPerBlock);

meanRewardPerBlock=zeros(1,blocks);
varRewardPerBlock=zeros(1,blocks);

for block=1:blocks
    varRewardPerBlock(1,block)=var(mean(Reward(:,1+(block-1)*trialsPerBlock:block*trialsPerBlock),2));
    meanRewardPerBlock(1,block)=mean(mean(Reward(:,1+(block-1)*trialsPerBlock:block*trialsPerBlock),2));
end

%p1 = plot(meanRewardPerBlock, '-ks','LineWidth',2,'MarkerFaceColor', [0 0 0], 'MarkerSize', 18);



%Learning curve

figure(1)
errorbar(meanRewardPerBlock*100,varRewardPerBlock*100,'-ks')
hold on


xlabel('Block','fontsize',18);
ylabel('% Correct Choice','fontsize',18);
set(gca,'fontsize',18);
axis([1-0.5 blocks+0.5 0 100])
axis square
ax = gca;
#ax.YTick = [0 25 50 75 100];





%Histogram for learning and transfer learning


lastBlockReward=Reward(:,1+(blocks-1)*trialsPerBlock:blocks*trialsPerBlock);


A=rewardedStimulus(1,1+(blocks-1)*trialsPerBlock:blocks*trialsPerBlock)==1;
learingHist(1,1)=mean(mean(lastBlockReward(:,A~=0)))*100; %expressed as 100%
learingHist(1,2)=(1-mean(mean(lastBlockReward(:,A~=0))))*100;

B=rewardedStimulus(1,1+(blocks-1)*trialsPerBlock:blocks*trialsPerBlock)==2;
learingHist(2,1)=mean(mean(lastBlockReward(:,B~=0)))*100;
learingHist(2,2)=(1-mean(mean(lastBlockReward(:,B~=0))))*100;

tA=transRewardedStimulus==1;
transLearingHist(1,1)=mean(mean(transReward(:,tA)))*100;
transLearingHist(1,2)=(1-mean(mean(transReward(:,tA))))*100;

tB=transRewardedStimulus==2;
transLearingHist(2,1)=mean(mean(transReward(:,tB)))*100;
transLearingHist(2,2)=(1-mean(mean(transReward(:,tB))))*100;

figure(2)

barLocations =[ 0.85, 1.15 , 1.85, 2.15];
barColors =[ 'k', 'r', 'r', 'k' ];
barLength =0.25;



temp=learingHist';
temp=temp(:);

for i=1:length(barLocations)
    bar(barLocations(i),temp(i),barLength,barColors(i)); 
    hold on;
end

xlabel('Rewarded Stimulus','fontsize',18);
ylabel('% Correct Choices','fontsize',18);
set(gca,'fontsize',18);
axis([ 0.5 2.5  0 100])
axis square
ax = gca;
%ax.XTickLabel = {'Mango' 'Lemon'}; This doesn't work
%ax.YTick = [0 25 50 75 100];
%ax.XTick =  [1 2];

legend('preference for stimulus 1', 'preference for stimulus 2');


figure(3)

barLocations =[ 0.85, 1.15 , 1.85, 2.15];
barColors =[ 'b', 'c', 'c', 'b' ];
barLength =0.25;


temp=transLearingHist';
temp=temp(:);

for i=1:length(barLocations)
    bar(barLocations(i),temp(i),barLength,barColors(i)); 
    hold on;
end

xlabel('Rewarded Transfer Stimulus','fontsize',18);
ylabel('% Correct Choices','fontsize',18);
set(gca,'fontsize',18);
axis([ 0.5 2.5  0 100])
axis square
ax = gca;
%ax.YTick = [0 25 50 75 100];
%ax.XTick =  [1 2];

legend('preference for stimulus 1', 'preference for stimulus 2');



%Weights after Leanring and Transfer Learning

% figure(5)
% % meanWeightLearning=mean(W32Learning,3);
% % varWeightLearning=var(W32Learning,[],3);
% % 
% % subplot(1,2,1)
% % errorbar(meanWeightLearning(1,:), varWeightLearning(1,:));
% 
% 
% subplot(1,2,1)
% 
% colormap hot
% imagesc(mean(W32Learning,3));
% 
% caxis manual
% caxis([minWeight maxWeight]);
% hold on;
% axis square
% ax = gca;
% ax.XTick = [ 1 2];
% ax.YTick = [ 1 2];
% set(gca,'fontsize',18);
% xlabel('Learning','fontsize',18);
% 
% subplot(1,2,2)
% imagesc(mean(W32TransferLearning,3));
% axis square
% ax = gca;
% ax.XTick = [ 1 2];
% ax.YTick = [ 1 2];
% set(gca,'fontsize',18);
% 
% caxis manual
% caxis([minWeight maxWeight]);
% xlabel('Transfer Learning','fontsize',18);
% 
% colorbar('location','Manual', 'position', [0.93 0.25 0.02 0.53]);




%Learning curve for delayed not match to sample


meanRewardPerBlock2=zeros(1,blocks);
varRewardPerBlock2=zeros(1,blocks);

for block=1:blocks
    varRewardPerBlock2(1,block)=var(mean(notMatchToSampleReward(:,1+(block-1)*trialsPerBlock:block*trialsPerBlock),2));
    meanRewardPerBlock2(1,block)=mean(mean(notMatchToSampleReward(:,1+(block-1)*trialsPerBlock:block*trialsPerBlock),2));
end


figure(4)
errorbar(meanRewardPerBlock2*100,varRewardPerBlock2*100,'-ks')
hold on
%hline = refline([0 50]);
%hline.Color = 'k';
%set(hline,'LineStyle','--','LineWidth',2)

xlabel('Block','fontsize',18);
ylabel('% Correct Choice','fontsize',18);
title('Delayed Not Match to Sample','fontsize',18);
set(gca,'fontsize',18);
axis([1-0.5 blocks+0.5 0 100])
axis square
ax = gca;
%ax.YTick = [0 25 50 75 100];



%Histogram for learning and transfer learning NMTS

lastBlockReward=notMatchToSampleReward(:,1+(blocks-1)*trialsPerBlock:blocks*trialsPerBlock);

A=rewardedStimulus(1,1+(blocks-1)*trialsPerBlock:blocks*trialsPerBlock)==1;
learingHist(1,1)=mean(mean(lastBlockReward(:,A~=0)))*100; %expressed as 100%
learingHist(1,2)=(1-mean(mean(lastBlockReward(:,A~=0))))*100;

B=rewardedStimulus(1,1+(blocks-1)*trialsPerBlock:blocks*trialsPerBlock)==2;
learingHist(2,1)=mean(mean(lastBlockReward(:,B~=0)))*100;
learingHist(2,2)=(1-mean(mean(lastBlockReward(:,B~=0))))*100;

tA=transRewardedStimulus==1;
transLearingHist(1,1)=mean(mean(transnotMatchToSampleReward(:,tA)))*100;
transLearingHist(1,2)=(1-mean(mean(transnotMatchToSampleReward(:,tA))))*100;

tB=transRewardedStimulus==2;
transLearingHist(2,1)=mean(mean(transnotMatchToSampleReward(:,tB)))*100;
transLearingHist(2,2)=(1-mean(mean(transnotMatchToSampleReward(:,tB))))*100;

figure(5)

barLocations =[ 0.85, 1.15 , 1.85, 2.15];
barColors =[ 'k', 'r', 'r', 'k' ];
barLength =0.25;



temp=learingHist';
temp=temp(:);

for i=1:length(barLocations)
    bar(barLocations(i),temp(i),barLength,barColors(i)); 
    hold on;
end

xlabel('Rewarded NM Stimulus','fontsize',18);
ylabel('% Correct Choices','fontsize',18);
set(gca,'fontsize',18);
axis([ 0.5 2.5  0 100])
axis square
ax = gca;
%ax.XTickLabel = {'Mango' 'Lemon'}; This doesn't work
%ax.YTick = [0 25 50 75 100];
%ax.XTick =  [1 2];

legend('preference for stimulus 1', 'preference for stimulus 2');


figure(6)

barLocations =[ 0.85, 1.15 , 1.85, 2.15];
barColors =[ 'b', 'c', 'c', 'b' ];
barLength =0.25;


temp=transLearingHist';
temp=temp(:);

for i=1:length(barLocations)
    bar(barLocations(i),temp(i),barLength,barColors(i)); 
    hold on;
end

xlabel('Rewarded NM Transfer Stimulus','fontsize',18);
ylabel('% Correct Choices','fontsize',18);
set(gca,'fontsize',18);
axis([ 0.5 2.5  0 100])
axis square
ax = gca;
%ax.YTick = [0 25 50 75 100];
%ax.XTick =  [1 2];

legend('preference for stimulus 1', 'preference for stimulus 2');

% file output

meanRewardPerBlock = [meanRewardPerBlock, mean(mean(transReward(:,1~=0)))];
varRewardPerBlock = [varRewardPerBlock, var(mean(transReward(:,1~=0)))];


meanRewardPerBlock2 = [meanRewardPerBlock2, mean(mean(transnotMatchToSampleReward(:,1~=0)))];
varRewardPerBlock2 = [varRewardPerBlock2, var(mean(transnotMatchToSampleReward(:,1~=0)))];


temp =[[1,2,3,4,5,6,7]' meanRewardPerBlock' varRewardPerBlock'];
csvwrite('dmtsli5.csv',temp);
temp2 =[[1,2,3,4,5,6,7]' meanRewardPerBlock2' varRewardPerBlock2'];
csvwrite('dnmtsli5.csv',temp2);
