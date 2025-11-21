% Filter 9
% Pass 0.10
% Stop 0.15
% Num taps = 60 (order = num_taps - 1 = 59)

pass = 0.10;
stop = 0.15;
num_taps = 60;
order = num_taps - 1;
f = [0 pass stop 1];
a = [1 1 0 0];

coeff = remez(order, f, a);

q = quantizer('fixed', 'floor', 'saturate', [16, 16]);

quantized_coeff = quantize(q, coeff);

[h,w] = freqz(quantized_coeff,1,2048);

plot(f,a,w/pi,abs(h))
legend('Ideal','firpm Design')
xlabel 'Radian Frequency (\omega/\pi)', ylabel 'Magnitude'