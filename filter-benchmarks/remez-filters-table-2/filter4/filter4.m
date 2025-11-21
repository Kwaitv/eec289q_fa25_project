% Filter 4
% Pass 0.20
% Stop 0.25
% Num taps = 80 (order = num_taps - 1 = 79)

pass = 0.20;
stop = 0.25;
num_taps = 80;
order = num_taps - 1;
f = [0 pass stop 1];
a = [1 1 0 0];

coeff = remez(order, f, a);

q = quantizer('fixed', 'floor', 'saturate', [12, 12]);

quantized_coeff = quantize(q, coeff);

[h,w] = freqz(quantized_coeff,1,2048);

plot(f,a,w/pi,abs(h))
legend('Ideal','firpm Design')
xlabel 'Radian Frequency (\omega/\pi)', ylabel 'Magnitude'