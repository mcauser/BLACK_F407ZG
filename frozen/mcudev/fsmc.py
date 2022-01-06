import machine
import stm

RCC_AHB3ENR_FSMCEN  = const(0x01)
RCC_AHB1ENR_GPIODEN = const(0x08)
RCC_AHB1ENR_GPIOEEN = const(0x10)
RCC_AHB1ENR_GPIOFEN = const(0x20)
RCC_AHB1ENR_GPIOGEN = const(0x40)
FSMC_Banks_base = const(0xA0000000)
FSMC_BCR_bank1_offset = const(0x0)
FSMC_BTR_bank1_offset = const(0x4)
FSMC_BCR_bank2_offset = const(0x8)
FSMC_BTR_bank2_offset = const(0xC)
FSMC_BCR_bank3_offset = const(0x10)
FSMC_BTR_bank3_offset = const(0x14)
FSMC_BCR_bank4_offset = const(0x18)
FSMC_BTR_bank4_offset = const(0x1c)
FSMC_BCRx_MWID_8bit  = const(0x00000000)
FSMC_BCRx_MWID_16bit = const(0x00000010)
FSMC_BCRx_WREN = const(0x00001000)
FSMC_BCRx_MBKEN = const(0x1)

LCD_REG = const(0x60000000)
LCD_RAM = const(0x60080000)

LCD_Zx_REG = const(0x6C000000)
LCD_Zx_RAM = const(0x6C000080)

@micropython.viper
def _mem_SET(addr,data):
        _tmp = data
        machine.mem32[addr] = _tmp
        
@micropython.viper
def _mem_OR(addr,data):
        _tmp = data
        machine.mem32[addr] |= _tmp
        
@micropython.viper
def _mem_AND_OR(addr,anddata,data):
        _tmp = anddata
        machine.mem32[addr] &= _tmp
        _tmp = data
        machine.mem32[addr] |= _tmp
        
#class MCU_DevF4Zx_Display():
class FSMC_Display_Zx():
    def __init__(self):
        self.FSMC_BTR1_ADDSET_T = 0x00000001  # ILI9341, 90ns
        self.FSMC_BTR1_DATAST_T = 0x00000400  # HCLK cycles
        self.FSMC_BTR1_ADDHLD_T = 0x00000010
        self.FSMC_BTR3_ADDSET_T = 0x00000000
        self.FSMC_BTR3_DATAST_T = 0x00000000
        self.FSMC_BTR3_ADDHLD_T = 0x00000000
        
    @micropython.viper
    def init_fsmc_disp(self):
        _mem_OR(stm.RCC + stm.RCC_AHB3ENR,RCC_AHB3ENR_FSMCEN) # FSMC clock enable
        _mem_OR(stm.RCC + stm.RCC_AHB1ENR, RCC_AHB1ENR_GPIODEN | RCC_AHB1ENR_GPIOEEN | \
                                                RCC_AHB1ENR_GPIOFEN | RCC_AHB1ENR_GPIOGEN) # GPIO clock Enable
        _mem_AND_OR(stm.GPIOD + stm.GPIO_MODER,0b10101010101010101011101011111010,0b10101010101010101000101000001010)
        #machine.mem32[stm.GPIOD + stm.GPIO_MODER] = 0b10101010101010101000101000001010
        _mem_AND_OR(stm.GPIOE + stm.GPIO_MODER,0b10101010101010101011111111111010,0b10101010101010101000000000001010)
        #machine.mem32[stm.GPIOE + stm.GPIO_MODER] = 0b10101010101010101000000000001010
        _mem_AND_OR(stm.GPIOF + stm.GPIO_MODER,0b10101010111111111111101010101010,0b10101010000000000000101010101010)
        #machine.mem32[stm.GPIOF + stm.GPIO_MODER] = 0b10101010000000000000101010101010
        _mem_AND_OR(stm.GPIOG + stm.GPIO_MODER,0b11111110111011111111101010101010,0b00000010001000000000101010101010)
        #machine.mem32[stm.GPIOG + stm.GPIO_MODER] = 0b00000010001000000000101010101010
        machine.mem32[stm.GPIOD + stm.GPIO_OSPEEDR] = 0xFFFFFFFF  # 0x54154525
        machine.mem32[stm.GPIOE + stm.GPIO_OSPEEDR] = 0xFFFFFFFF  # 0x55554000
        machine.mem32[stm.GPIOF + stm.GPIO_OSPEEDR] = 0xFFFFFFFF  #
        machine.mem32[stm.GPIOG + stm.GPIO_OSPEEDR] = 0xFFFFFFFF  #
        # Alternate Function = FSMC = (0x0C) = 12
        _mem_AND_OR(stm.GPIOD + stm.GPIO_AFR0,0xFFCCFFCC,0x00CC00CC)
        #machine.mem32[stm.GPIOD + stm.GPIO_AFR0] =  0x00CC00CC
        machine.mem32[stm.GPIOD + stm.GPIO_AFR1] =  0xCCCCCCCC 
        _mem_AND_OR(stm.GPIOE + stm.GPIO_AFR0,0xCFFFFFCC,0xC00000CC)
        #machine.mem32[stm.GPIOE + stm.GPIO_AFR0] =  0xC00000CC
        machine.mem32[stm.GPIOE + stm.GPIO_AFR1] =  0xCCCCCCCC
        _mem_AND_OR(stm.GPIOF + stm.GPIO_AFR0,0xFFCCCCCC,0x00CCCCCC)
        #machine.mem32[stm.GPIOF + stm.GPIO_AFR0] =  0x00CCCCCC
        _mem_AND_OR(stm.GPIOF + stm.GPIO_AFR1,0xCCCCFFFF,0xCCCC0000)
        #machine.mem32[stm.GPIOF + stm.GPIO_AFR1] =  0xCCCC0000
        _mem_AND_OR(stm.GPIOG + stm.GPIO_AFR0,0xFFCCCCCC,0x00CCCCCC)
        #machine.mem32[stm.GPIOG + stm.GPIO_AFR0] =  0x00CCCCCC
        _mem_AND_OR(stm.GPIOG + stm.GPIO_AFR1,0xFFFCFCFF,0x000C0C00)
        #machine.mem32[stm.GPIOG + stm.GPIO_AFR1] =  0x000C0C00
        
        machine.mem32[FSMC_Banks_base + FSMC_BTR_bank4_offset] = self.FSMC_BTR1_ADDSET_T | self.FSMC_BTR1_DATAST_T | self.FSMC_BTR1_ADDHLD_T # | FSMC_BTR1_CLKDIV_1 | FSMC_BTR1_ACCMOD
        _mem_SET(FSMC_Banks_base + FSMC_BCR_bank4_offset,FSMC_BCRx_MWID_16bit | FSMC_BCRx_WREN | FSMC_BCRx_MBKEN)
    
    @micropython.viper
    def init_fsmc_ram(self):
        _mem_OR(stm.RCC + stm.RCC_AHB3ENR,RCC_AHB3ENR_FSMCEN)
        _mem_OR(stm.RCC + stm.RCC_AHB1ENR, RCC_AHB1ENR_GPIODEN | RCC_AHB1ENR_GPIOEEN | \
                                                RCC_AHB1ENR_GPIOFEN | RCC_AHB1ENR_GPIOGEN) # GPIO clock Enable
        _mem_AND_OR(stm.GPIOD + stm.GPIO_MODER,0b10101010101010101011101011111010,0b10101010101010101000101000001010)
        #machine.mem32[stm.GPIOD + stm.GPIO_MODER] = 0b10101010101010101000101000001010
        _mem_AND_OR(stm.GPIOE + stm.GPIO_MODER,0b10101010101010101011111111111010,0b10101010101010101000000000001010)
        #machine.mem32[stm.GPIOE + stm.GPIO_MODER] = 0b10101010101010101000000000001010
        _mem_AND_OR(stm.GPIOF + stm.GPIO_MODER,0b10101010111111111111101010101010,0b10101010000000000000101010101010)
        #machine.mem32[stm.GPIOF + stm.GPIO_MODER] = 0b10101010000000000000101010101010
        _mem_AND_OR(stm.GPIOG + stm.GPIO_MODER,0b11111110111011111111101010101010,0b00000010001000000000101010101010)
        #machine.mem32[stm.GPIOG + stm.GPIO_MODER] = 0b00000010001000000000101010101010
        machine.mem32[stm.GPIOD + stm.GPIO_OSPEEDR] = 0xFFFFFFFF
        machine.mem32[stm.GPIOE + stm.GPIO_OSPEEDR] = 0xFFFFFFFF
        machine.mem32[stm.GPIOF + stm.GPIO_OSPEEDR] = 0xFFFFFFFF
        machine.mem32[stm.GPIOG + stm.GPIO_OSPEEDR] = 0xFFFFFFFF
        _mem_AND_OR(stm.GPIOD + stm.GPIO_AFR0,0xFFCCFFCC,0x00CC00CC)
        #machine.mem32[stm.GPIOD + stm.GPIO_AFR0] =  0x00CC00CC
        machine.mem32[stm.GPIOD + stm.GPIO_AFR1] =  0xCCCCCCCC 
        _mem_AND_OR(stm.GPIOE + stm.GPIO_AFR0,0xCFFFFFCC,0xC00000CC)
        #machine.mem32[stm.GPIOE + stm.GPIO_AFR0] =  0xC00000CC
        machine.mem32[stm.GPIOE + stm.GPIO_AFR1] =  0xCCCCCCCC
        _mem_AND_OR(stm.GPIOF + stm.GPIO_AFR0,0xFFCCCCCC,0x00CCCCCC)
        #machine.mem32[stm.GPIOF + stm.GPIO_AFR0] =  0x00CCCCCC
        _mem_AND_OR(stm.GPIOF + stm.GPIO_AFR1,0xCCCCFFFF,0xCCCC0000)
        #machine.mem32[stm.GPIOF + stm.GPIO_AFR1] =  0xCCCC0000
        _mem_AND_OR(stm.GPIOG + stm.GPIO_AFR0,0xFFCCCCCC,0x00CCCCCC)
        #machine.mem32[stm.GPIOG + stm.GPIO_AFR0] =  0x00CCCCCC
        _mem_AND_OR(stm.GPIOG + stm.GPIO_AFR1,0xFFFCFCFF,0x000C0C00)
        #machine.mem32[stm.GPIOG + stm.GPIO_AFR1] =  0x000C0C00
        machine.mem32[FSMC_Banks_base + FSMC_BTR_bank3_offset] = self.FSMC_BTR3_ADDSET_T | self.FSMC_BTR3_DATAST_T | self.FSMC_BTR3_ADDHLD_T
        _mem_SET(FSMC_Banks_base + FSMC_BCR_bank3_offset, FSMC_BCRx_MWID_16bit | FSMC_BCRx_WREN | FSMC_BCRx_MBKEN)
        
#class MCU_DevF4Zx_SRAM():
class FSMC_SRAM():
    def __init__(self):
        self.FSMC_BTR3_ADDSET_T = 0x00000000
        self.FSMC_BTR3_DATAST_T = 0x00000000
        self.FSMC_BTR3_ADDHLD_T = 0x00000000

    @micropython.viper
    def init_fsmc_ram(self):
        _mem_OR(stm.RCC + stm.RCC_AHB3ENR,RCC_AHB3ENR_FSMCEN)
        _mem_OR(stm.RCC + stm.RCC_AHB1ENR, RCC_AHB1ENR_GPIODEN | RCC_AHB1ENR_GPIOEEN | \
                                                RCC_AHB1ENR_GPIOFEN | RCC_AHB1ENR_GPIOGEN) # GPIO clock Enable
        machine.mem32[stm.GPIOD + stm.GPIO_MODER] = 0b10101010101010101000101000001010
        machine.mem32[stm.GPIOE + stm.GPIO_MODER] = 0b10101010101010101000000000001010
        machine.mem32[stm.GPIOF + stm.GPIO_MODER] = 0b10101010000000000000101010101010
        machine.mem32[stm.GPIOG + stm.GPIO_MODER] = 0b00000010001000000000101010101010
        machine.mem32[stm.GPIOD + stm.GPIO_OSPEEDR] = 0xFFFFFFFF
        machine.mem32[stm.GPIOE + stm.GPIO_OSPEEDR] = 0xFFFFFFFF
        machine.mem32[stm.GPIOF + stm.GPIO_OSPEEDR] = 0xFFFFFFFF
        machine.mem32[stm.GPIOG + stm.GPIO_OSPEEDR] = 0xFFFFFFFF
        machine.mem32[stm.GPIOD + stm.GPIO_AFR0] =  0x00CC00CC
        machine.mem32[stm.GPIOD + stm.GPIO_AFR1] =  0xCCCCCCCC 
        machine.mem32[stm.GPIOE + stm.GPIO_AFR0] =  0xC00000CC
        machine.mem32[stm.GPIOE + stm.GPIO_AFR1] =  0xCCCCCCCC
        machine.mem32[stm.GPIOF + stm.GPIO_AFR0] =  0x00CCCCCC
        machine.mem32[stm.GPIOF + stm.GPIO_AFR1] =  0xCCCC0000
        machine.mem32[stm.GPIOG + stm.GPIO_AFR0] =  0x00CCCCCC
        machine.mem32[stm.GPIOG + stm.GPIO_AFR1] =  0x000C0C00
        machine.mem32[FSMC_Banks_base + FSMC_BTR_bank3_offset] = self.FSMC_BTR3_ADDSET_T | self.FSMC_BTR3_DATAST_T | self.FSMC_BTR3_ADDHLD_T
        _mem_SET(FSMC_Banks_base + FSMC_BCR_bank3_offset, FSMC_BCRx_MWID_16bit | FSMC_BCRx_WREN | FSMC_BCRx_MBKEN)


#class MCU_DevF4Vx_Display():
class FSMC_Display_Vx():
    def __init__(self):
        _mem_OR(stm.RCC + stm.RCC_AHB3ENR,RCC_AHB3ENR_FSMCEN)
        _mem_OR(stm.RCC + stm.RCC_AHB1ENR, RCC_AHB1ENR_GPIODEN | RCC_AHB1ENR_GPIOEEN)
        self.FSMC_BTR1_ADDSET_T = 0x00000001
        self.FSMC_BTR1_DATAST_T = 0x00000400
        self.FSMC_BCR1_MWID_0 = 0x00000010
        self.FSMC_BCR1_WREN = 0x00001000
        self.FSMC_BCR1_MBKEN = 0x1
        self.FSMC_BTR1_ADDHLD_0 = 0x00000010

    @micropython.viper
    def init_fsmc_disp(self):
        _mem_OR(stm.RCC + stm.RCC_AHB3ENR,RCC_AHB3ENR_FSMCEN)
        _mem_OR(stm.RCC + stm.RCC_AHB1ENR, RCC_AHB1ENR_GPIODEN | RCC_AHB1ENR_GPIOEEN)
        # 10 10 10 00 00 10 10 10 10 00 10 10 00 10 10 10
        machine.mem32[stm.GPIOD + stm.GPIO_MODER] = 0b10101000001010101000101000101010
        machine.mem32[stm.GPIOE + stm.GPIO_MODER] = 0xAAAA8000
        machine.mem32[stm.GPIOD + stm.GPIO_OSPEEDR] = 0xFFFFFFFF
        machine.mem32[stm.GPIOE + stm.GPIO_OSPEEDR] = 0xFFFFFFFF
        machine.mem32[stm.GPIOD + stm.GPIO_AFR0] =  ( (0b1100<<(4*0)) | (0b1100<<(4*1)) | (0b1100<<(4*2)) | (0b1100<<(4*4)) | (0b1100<<(4*5)) | (0b1100<<(4*7)) )
        machine.mem32[stm.GPIOD + stm.GPIO_AFR1] =  ( (0b1100<<(4*(8-8))) | (0b1100<<(4*(9-8))) | (0b1100<<(4*(10-8))) | (0b1100<<(4*(13-8))) | (0b1100<<(4*(14-8))) | (0b1100<<(4*(15-8))))
        machine.mem32[stm.GPIOE + stm.GPIO_AFR0] = 0b1100<<(4*7)
        machine.mem32[stm.GPIOE + stm.GPIO_AFR1] = 0xCCCCCCCC
        machine.mem32[FSMC_Banks_base + FSMC_BCR_bank1_offset] = self.FSMC_BTR1_ADDSET_T | self.FSMC_BTR1_DATAST_T | self.FSMC_BTR1_ADDHLD_0 # | FSMC_BTR1_CLKDIV_1 | FSMC_BTR1_ACCMOD
        _mem_SET(FSMC_Banks_base + FSMC_BCR_bank1_offset, FSMC_BCRx_MWID_16bit | FSMC_BCRx_WREN | FSMC_BCRx_MBKEN)
