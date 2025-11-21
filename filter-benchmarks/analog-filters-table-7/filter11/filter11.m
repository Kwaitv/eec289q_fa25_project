% Filter 11 (from Table 7)
% Pass 0.27
% Stop 0.29
% Num taps = 189 (order = num_taps - 1 = 188)

pass = 0.27;
stop = 0.29;
num_taps = 189;
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