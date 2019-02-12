module gsr_pur_assign(output wire gsr, output reg pur);
	initial begin
		pur = 1'b0;
		#5;
		pur = 1'b1;
	end
	assign gsr = 1'b1;
endmodule

module dqsbuf_tb();

	reg eclk, sclk;

	always #5 eclk = (eclk === 1'b0);
	always #10 sclk = (sclk === 1'b0);

	reg reset = 1'b1, pause = 1'b0, read0 = 1'b0, read1 = 1'b0;

	reg [2:0] rclksel = 3'b010;
	reg [7:0] dyndelay = 8'h00;
	reg rdloadn = 1'b1, rdmove = 1'b0, rddirection = 1'b0;
	reg wrloadn = 1'b1, wrmove = 1'b0, wrdirection = 1'b0;

	reg dqsi = 1'b0, dq = 1'b0;

	initial begin
		$dumpfile("dqsbuf_tb.vcd");
		$dumpvars(0, dqsbuf_tb);

		repeat (5) @(posedge sclk);

		reset = 1'b0;

		repeat (30) @(posedge sclk);

		{read1, read0} = 2'b11;
		repeat (2) @(posedge sclk);
		{read1, read0} = 2'b00;

		repeat (2) begin
			dq = 1'b0;
			#2.5;
			dqsi = 1'b1;
			#2.5;
			dq = 1'b1;
			#2.5;
			dqsi = 1'b0;
			#2.5;

			dq = 1'b0;
			#2.5;
			dqsi = 1'b1;
			#2.5;
			dq = 1'b1;
			#2.5;
			dqsi = 1'b0;
			#2.5;

			dq = 1'b1;
			#2.5;
			dqsi = 1'b1;
			#2.5;
			dq = 1'b0;
			#2.5;
			dqsi = 1'b0;
			#2.5;

			dq = 1'b1;
			#2.5;
			dqsi = 1'b1;
			#2.5;
			dq = 1'b0;
			#2.5;
			dqsi = 1'b0;
			#2.5;
		end

		repeat (30) @(posedge sclk);

		$finish;
	end


	wire dqsr90, dqsw, dqsw270;
	wire [2:0] rdpntr, wrpntr;

	DQSBUFM dqsbuf_i (
		.DQSI(dqsi),
		.ECLK(eclk), .SCLK(sclk), .RST(reset), .PAUSE(pause),
		.WRLOADN(wrloadn), .WRMOVE(wrmove), .WRDIRECTION(wrdirection),
		.RDLOADN(rdloadn), .RDMOVE(rdmove), .RDDIRECTION(rddirection),
	 	.READ0(read0), .READ1(read1), .READCLKSEL0(rclksel[0]), .READCLKSEL1(rclksel[1]), .READCLKSEL2(rclksel[2]),
	 	.DYNDELAY7(dyndelay[7]), .DYNDELAY6(dyndelay[6]), .DYNDELAY5(dyndelay[5]), .DYNDELAY4(dyndelay[4]),
	 	.DYNDELAY3(dyndelay[3]), .DYNDELAY2(dyndelay[2]), .DYNDELAY1(dyndelay[1]), .DYNDELAY0(dyndelay[0]), 
		.DQSW(dqsw), .DQSW270(dqsw270), .DQSR90(dqsr90),
		.RDPNTR0(rdpntr[0]), .RDPNTR1(rdpntr[1]), .RDPNTR2(rdpntr[2]), 
		.WRPNTR0(wrpntr[0]), .WRPNTR1(wrpntr[1]), .WRPNTR2(wrpntr[2])
	 );

	wire [3:0] dq_i;
	wire qwl;

	IDDRX2DQA iddr_i(
		.SCLK(sclk), .ECLK(eclk), .DQSR90(dqsr90), .RST(reset),
		.D(dq), .Q0(dq_i[0]), .Q1(dq_i[1]), .Q2(dq_i[2]), .Q3(dq_i[3]), .QWL(qwl),
		.RDPNTR0(rdpntr[0]), .RDPNTR1(rdpntr[1]), .RDPNTR2(rdpntr[2]), 
		.WRPNTR0(wrpntr[0]), .WRPNTR1(wrpntr[1]), .WRPNTR2(wrpntr[2])
	);

endmodule