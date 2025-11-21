% Filter 4 (from Table 7)
% Pass 0.25
% Stop 0.3
% Num taps = 28 (order = num_taps - 1 = 27)

pass = 0.25;
stop = 0.3;
num_taps = 28;
order = num_taps - 1;
f = [0 pass stop 1];
a = [1 1 0 0];

coeff = remez(order, f, a);

q = quantizer('fixed', 'floor', 'saturate', [24, 24]);

quantized_coeff = quantize(q, coeff);

bin_coeff = num2bin(q, quantized_coeff);

stringElements = cellstr(bin_coeff);
joinedString = strjoin(stringElements, ', ');
fprintf('[%s]\n', joinedString);

[h,w] = freqz(quantized_coeff,1,2048);

plot(f,a,w/pi,abs(h))
legend('Ideal','firpm Design')
xlabel 'Radian Frequency (\omega/\pi)', ylabel 'Magnitude'