% Filter 2
% Pass 0.1
% Stop 0.25
% Num taps = 100 (order = num_taps - 1 = 109)

pass = 0.1;
stop = 0.25;
num_taps = 100;
order = num_taps - 1;
f = [0 pass stop 1];
a = [1 1 0 0];

coeff = remez(order, f, a);

q = quantizer('fixed', 'floor', 'saturate', [10, 10]);

quantized_coeff = quantize(q, coeff)

[h,w] = freqz(quantized_coeff,1,2048);

plot(f,a,w/pi,abs(h))
legend('Ideal','firpm Design')
xlabel 'Radian Frequency (\omega/\pi)', ylabel 'Magnitude'