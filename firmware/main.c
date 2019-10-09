#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <irq.h>
#include <uart.h>
#include <console.h>

#include <generated/csr.h>
#include <generated/mem.h>
#include "sdram_bist.h"

#include <net/microudp.h>
#include <net/tftp.h>

static char *readstr(void)
{
	char c[2];
	static char s[64];
	static int ptr = 0;

	if(readchar_nonblock()) {
		c[0] = readchar();
		c[1] = 0;
		switch(c[0]) {
			case 0x7f:
			case 0x08:
				if(ptr > 0) {
					ptr--;
					putsnonl("\x08 \x08");
				}
				break;
			case 0x07:
				break;
			case '\r':
			case '\n':
				s[ptr] = 0x00;
				putsnonl("\n");
				ptr = 0;
				return s;
			default:
				if(ptr >= (sizeof(s) - 1))
					break;
				putsnonl(c);
				s[ptr] = c[0];
				ptr++;
				break;
		}
	}

	return NULL;
}

static char *get_token(char **str)
{
	char *c, *d;

	c = (char *)strchr(*str, ' ');
	if(c == NULL) {
		d = *str;
		*str = *str+strlen(*str);
		return d;
	}
	*c = 0;
	d = *str;
	*str = c+1;
	return d;
}

static void prompt(void)
{
	printf("RUNTIME>");
}

static void help(void)
{
	puts("Available commands:");
	puts("h help                            - this command");
	puts("o loadsound                       - load sound.bin");
	puts("l lastaddr                        - last address used");
	puts("p printhdr                        - loaded sound.bin header");
	puts("r reboot                          - reboot CPU");
	puts("");
#ifdef CSR_SDRAM_GENERATOR_BASE
	puts("sdram_bist burst_length [random]- stress & test SDRAM from HW");
#endif
}

static void reboot(void)
{
	ctrl_reset_write(1);
}

static const unsigned char macadr[6] = {0x10, 0xe2, 0xd5, 0x00, 0x00, 0x00};

#define SOUND_RAM_BASE		MAIN_RAM_BASE + 0x100000
void loadsound(void);
void loadsound(void)
{
	unsigned int localip  = IPTOINT(192, 168, 1, 50);
	unsigned int remoteip = IPTOINT(192, 168, 1, 100);
	microudp_start(macadr, localip);

	tftp_get(remoteip, 69, "sound.bin", (void *)SOUND_RAM_BASE);
}

void lastaddr(void);
void lastaddr(void)
{
	unsigned int lastaddr = romemu_lst_addr_read();
	printf("Last address: 0x%08x\n", lastaddr);
}

void printhdr(void);
void printhdr(void)
{
	printf("Header:\n");
	for (int i = 0; i < 32; i++) {
		unsigned char *addr = (unsigned char *)(SOUND_RAM_BASE + i);
		printf("%02x ", *addr);
	}
	printf("\n");
}

static void console_service(void)
{
	char *str;
	char *token;

	str = readstr();
	if(str == NULL) return;
	token = get_token(&str);
	if((strcmp(token, "help") == 0) ||
	   (strcmp(token, "h") == 0))
		help();
	else if((strcmp(token, "lastaddr") == 0) ||
	        (strcmp(token, "l") == 0))
		lastaddr();
	else if((strcmp(token, "printhdr") == 0) ||
	        (strcmp(token, "p") == 0))
		printhdr();
	else if((strcmp(token, "loadsound") == 0) ||
	        (strcmp(token, "o") == 0))
		loadsound();
	else if((strcmp(token, "reboot") == 0) ||
	        (strcmp(token, "r") == 0))
		reboot();
#ifdef CSR_SDRAM_GENERATOR_BASE
	else if(strcmp(token, "sdram_bist") == 0) {
		unsigned int burst_length;
		unsigned int random;
		burst_length = atoi(get_token(&str));
		random = atoi(get_token(&str));
		if (burst_length == 0)
			burst_length = 128; /* default to 128 if not specified */
		printf("Executing SDRAM BIST with burst_length=%d and random=%d\n", burst_length, random);
		sdram_bist(burst_length, random);
	}
#endif
	prompt();
}

int main(void)
{
	irq_setmask(0);
	irq_setie(1);
	uart_init();

	puts("\nVersa ECP5 CPU testing software built "__DATE__" "__TIME__);
	prompt();

	while(1) {
		console_service();
	}

	return 0;
}
