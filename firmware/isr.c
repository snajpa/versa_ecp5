#include <generated/mem.h>
#include <generated/csr.h>
#include <irq.h>
#include <uart.h>

extern void periodic_isr(void);

#define SOUND_RAM_BASE		MAIN_RAM_BASE + 0x100000

void romemu_isr(void);
void romemu_isr(void)
{
	unsigned char *data = (unsigned char *)(romemu_req_addr_read() + SOUND_RAM_BASE);
	romemu_ans_data_write(*data);
	romemu_ev_enable_write(1);
}

void isr(void);
void isr(void)
{
	unsigned int irqs;

	irqs = irq_pending() & irq_getmask();

	if(irqs & (1 << ROMEMU_INTERRUPT))
		romemu_isr();

	if(irqs & (1 << UART_INTERRUPT))
		uart_isr(); 
}
