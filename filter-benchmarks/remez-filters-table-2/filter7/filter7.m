% Filter 7
% Pass 0.15
% Stop 0.20
% Num taps = 60 (order = num_taps - 1 = 59)

pass = 0.15;
stop = 0.20;
num_taps = 60;
order = num_taps - 1;
f = [0 pass stop 1];
a = [1 1 0 0];

coeff = remez(order, f, a);

q = quantizer('fixed', 'floor', 'saturate', [14, 14]);

quantized_coeff = quantize(q, coeff);

[h,w] = freqz(quantized_coeff,1,2048);

plot(f,a,w/pi,abs(h))
legend('Ideal','firpm Design')
xlabel 'Radian Frequency (\omega/\pi)', ylabel 'Magnitude'