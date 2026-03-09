This is a review of the course so far, running through sections 
- [[§5.1 Areas & Distances]] 
- [[§5.2- Definite Integrals]]
- [[§5.3 The Fundamental Theorem of Calculus]]
- [[§5.4 Indefinite Integrals]]
- [[§5.5 The Substitution Rule]]
- [[§6.1 Area Between Curves]]
- [[§6.2 Volumes of Rotation]]
- [[§6.5 Average Value of a Function]]
There are also handwritten solutions to a [[2B-Midterm1-Sample.pdf|practice midterm]] from several quarters ago available [[2B-Midterm1-Sample solutions.pdf|here]].

> [!example] Problem (**Challenge**)
> [Challenge] Evaluate the limit:
> $$
> \lim_{n \to \infty} \sum_{i = 1}^n \left ( \frac{i^4}{n^5} + \frac{i}{n^2} \right )
> $$
>> [!success]- Solution
>> The trick here is to evaluate this as an integral. First, factor out $1/n$ from the summand:
>> $$\frac{i^4}{n^5} + \frac{i}{n^2} = \frac1n \left (  (i/n)^4 + (i/n) \right )$$
>> from here, we see that $a = 0$, $\Delta x = 1/n$ so $b = 1$. We’re home free when we write down:
>> $$\int_0^1 x^4 + x dx = \left [ \frac{x^5}{5} + \frac{x^2}{2} \right ]_0^1 = \frac{1}{5} + \frac12 = \frac{7}{10}$$
>> For more, see [[§5.1 Areas & Distances]] and [[§5.2- Definite Integrals]]

> [!example] Problem
> Compute the following antiderivative:
> $$
> \int \cos^2 (x) - \sin^2(x) dx
> $$
>> [!success]- Solution
>> Use difference of squares and then $u$ substitution. For more, see [[§5.5 The Substitution Rule]]

> [!example] Problem
> The area of the region bounded by the curve $y=e^{2 x}$, the $x$-axis, the $y$-axis, and the line $x=2$
>> [!success]- Solution
>> C: $\frac{e^4}{2}-\frac{1}{2}$ square units
>> $$\begin{aligned}A & =\int_0^2 e^{2 x} d x=\frac{1}{2} \int_0^2 e^{2 x}(2) d x \\& =\frac{1}{2}\left[e^{2 x}\right]_0^2 \\& =\frac{1}{2}\left(e^4-e^0\right) \\& =\frac{e^4-1}{2} \\& =\frac{e^4}{2}-\frac{1}{2}\end{aligned}$$
>> For more, see [[§6.1 Area Between Curves]]

> [!example] Problem
> The average value of $y=e^{3 x}$ over the interval from $x=0$ to $x=4$ is
>> [!success]- Solution
>> $$ \begin{aligned} \text { average value } & =\frac{1}{b-a} \int_a^b f(x) d x \\& =\frac{1}{4-0} \int_0^4 e^{3 x} d x \\ & =\frac{1}{4} \cdot \frac{1}{3} \int_0^4 e^{3 x} \cdot 3 d x \\ & =\frac{1}{12}\left[e^{3 x}\right]_0^4 \\ & =\frac{1}{12}\left(e^{12}-e^0\right) \\ & =\frac{e^{12}-1}{12}\end{aligned}$$
>> For more, see [[§6.5 Average Value of a Function]]

> [!example] Problem
> Which of the following is equivalent to
> $$
> \lim _{n \rightarrow \infty} \sum_{i=1}^n\left[\left(1+\frac{2 i}{n}\right)^2+1\right]\left(\frac{2}{n}\right) ?
> $$
> - A. $\int_2^4\left(x^2+1\right) d x$ 
> - B. $\int_1^3 x^2 d x$ 
> - C. $\int_1^2\left(x^2+1\right) d x$ 
> - D. $\int_1^3\left(x^2-1\right) d x$ 
> - E. $\int_1^3\left(x^2+1\right) d x$ 
>
>> [!success]- Solution
>> E. For more, see [[§5.2- Definite Integrals]]

> [!example] Problem
> 13. Let $A$ be the area bounded by one arch of the sine curve. Which of the following represents the volume of the solid generated when $A$ is revolved around the $x$-axis? \\
> - A. $2 \pi \int_0^\pi x \sin x d x$
> - B. $\pi \int_0^\pi \sin ^2 x d x$
> - C. $\pi \int_0^\pi x \sin x d x$
> - D. $\pi \int_0^{2 \pi} \sin ^2 x d x$
> - E. $2 \pi \int_0^1 \arcsin y d y$
> 
>> [!success]- Solution
>> B. For more, see [[§6.2 Volumes of Rotation]]

> [!example] Problem
> Approximate the value of $\int_1^3 \ln x d x$ using 4 circumscribed rectangles.
> - A. $1.007$
> - B. $1.296$
> - C. $1.557$
> - D. $2.015$
> - E. $3.114$
>
>> [!success]- Solution
> C
>> $$\begin{aligned}\text { Area } & \approx \frac{1}{2} \ln \frac{3}{2}+\frac{1}{2} \ln 2+\frac{1}{2} \ln \frac{5}{2}+\frac{1}{2} \ln 3 \\& =\frac{1}{2}\left(\ln \frac{3}{2}+\ln 2+\ln \frac{5}{2}+\ln 3\right) \\& \approx 1.557\end{aligned}$$
>> For more, see [[§5.2- Definite Integrals]]
