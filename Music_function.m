
function angle_est = Music_function(snapshots)   %snapshots 수를 입력해야함
temp = readmatrix('ant.csv');
temp_trnas = temp.';
DataMatrix = temp_trnas;

N=3;    %Number of array elements
K=snapshots;
% K=852;   %Number of data snapshots
d=0.28;   %Distance between elements in wavelengths
R=DataMatrix*DataMatrix'/K;
[doas,spec,specang] = musicdoa(R, 1);
[U,S,V]=svd(R);
[Q ,D]=eig(R);
[D,I]=sort(diag(D),1,'descend');   %Find r largest eigenvalues
Q=Q (:,I); %Sort the eigenvectors to put signal eigenvectors first 고유 벡터 재배열
%check the matrix to see how many column with zeros(or (i don't remember exactly and i don't have access to the data) maybe column with small values does it have and those are noises and the rest are signals in this code i had 3 signals )  
Qs=Q (:,1:1); %Get the signal eigenvectors
Qn=Q(:,2:N); %Get the noise eigenvectors
angles=(-90:0.1:90);
%Compute steering vectors corresponding values in angles
a1=exp(-i*2*pi*d*(0:N-1)'*sin((angles(:).')*pi/180));
for k=1:length(angles)
% Compute MUSIC ?spectrum?
music_spectrum(k)=1/(a1(:,k)'*Qn*Qn'*a1(:,k));
end
[pks, angle_est] = findpeaks(abs(music_spectrum), angles); % peak일때 각도 찾기
% plot(angles,abs(music_spectrum))
% grid on
% title('MUSIC Spectrum')
% xlabel('Angle in degrees')
end
