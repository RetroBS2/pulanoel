import pygame
from random import randint
from pygame.locals import *
from sys import exit
import os
import neat


geracao = 0
largura = 800
altura = 500

BACKGROUND = pygame.transform.scale(
    pygame.image.load('img/back.png'), (largura, altura))
CLOUD = pygame.transform.scale(
    pygame.image.load('img/clouds.png'), (largura, 300))


pygame.init()
tela = pygame.display.set_mode((largura, altura))


class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.x = 0
        self.y = altura - 170
        self.largura = 186
        self.altura = 128
        self.velocidade = 15
        self.sprites = [(pygame.image.load('img/Run (1).png')),
                        (pygame.image.load('img/Run (2).png')),
                        (pygame.image.load('img/Run (3).png')),
                        (pygame.image.load('img/Run (4).png')),
                        (pygame.image.load('img/Run (5).png')),
                        (pygame.image.load('img/Run (6).png')),
                        (pygame.image.load('img/Run (7).png')),
                        (pygame.image.load('img/Run (8).png')),
                        (pygame.image.load('img/Run (9).png')),
                        (pygame.image.load('img/Run (10).png')),
                        (pygame.image.load('img/Run (11).png'))]
        self.atual = 0
        self.image = self.sprites[self.atual]
        self.image = pygame.transform.scale(
            self.image, (self.largura, self.altura))
        self.rect = self.image.get_rect()
        self.rect.topleft = self.x, self.y
        self.vivo = True
        self.pulando = False
        self.pulo = 0
        self.noeis = []

    def update(self):
        for noel in self.noeis:
            if (noel[4]):
                self.atual += 0.05
                if (self.atual > len(self.sprites)-1):
                    self.atual = 0
                noel[3] = noel[1], noel[2]
                noel[0] = self.sprites[int(self.atual)]
                noel[0] = pygame.transform.scale(
                    noel[0], (self.largura, self.altura))
                tela.blit(noel[0], noel[3])

    def adicionarnoel(self):
        self.noeis.append([self.sprites[0], self.x, self.y, self.rect.topleft,
                          self.vivo, self.pulando, self.atual, self.pulo])

    def pula(self):
        for noel in self.noeis:
            if noel[5]:
                noel[7] += 0.5
                if noel[7] >= len(self.sprites):
                    noel[7] = 0
                    noel[5] = False
                    noel[2] = self.y
                if noel[7] < len(self.sprites)/2:
                    noel[2] -= self.velocidade
                else:
                    noel[2] += self.velocidade

    def colidir(self, chamine):
        arr = []
        for i, noel in enumerate(self.noeis):
            for gift in chamine.chamines:
                mask_pres = pygame.mask.from_surface(gift[0])
                rect_pres = gift[0].get_rect()
                mask = pygame.mask.from_surface(noel[0])
                distancia = (noel[1] - gift[1], noel[2] - gift[2])
                result = mask_pres.overlap(mask, distancia)
                if result:
                    if noel[4]:
                        noel[4] = False
                        self.noeis.pop(i)
                        arr.append(i)
        return arr


class Chamines():
    def __init__(self):
        self.pontos = 0
        self.altura = 115
        self.largura = 80
        self.limiteint = 1
        self.posx = largura + 20
        self.posy = altura - 155
        self.velocidade = 20
        self.intervalo = 0
        self.chamineimage = pygame.image.load('img/chamine.png')

        self.chamines = []
        self.chamines.append([self.chamineimage, self.posx,
                              self.posy])
        self.rect = self.chamines[0][0].get_rect()
        self.rect.topleft = self.posx, self.posy

    def movimentar(self):
        for cha in self.chamines:
            cha[1] -= self.velocidade/2
            image = pygame.transform.scale(cha[0], (self.largura, self.altura))
            tela.blit(image, (cha[1], cha[2]))

    def adicionarPresente(self):
        self.intervalo += self.limiteint
        if self.intervalo >= 100:
            self.chamines.append([self.chamineimage, self.posx, self.posy])
            self.intervalo = 0

    def removerPresente(self):
        for i, cha in enumerate(self.chamines):
            if cha[1] + self.largura * 5 < 0:
                self.chamines.pop(i)
                self.pontos += 1
                return 0.5
            else:
                return 0

    def dificuldade(self):
        if self.pontos >= 10:
            self.velocidade = 22

        if self.pontos >= 20:
            self.velocidade = 24

        if self.pontos >= 30:
            self.limiteint = 1.5

        if self.pontos >= 50:
            self.velocidade = 26
            self.limiteint = 2


def main(genomas, config):
    global geracao
    geracao += 1
    redes = []
    lista_genomas = []
    jogador = Jogador()
    noeis = []
    for _, genoma in genomas:
        rede = neat.nn.FeedForwardNetwork.create(genoma, config)
        redes.append(rede)
        genoma.fitness = 0
        lista_genomas.append(genoma)
        jogador.adicionarnoel()

    pygame.display.set_caption('Pula Noel')
    fonte = pygame.font.SysFont('arial', 30, True, True)

    chamine = Chamines()

    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        tela.fill((0, 0, 0))
        tela.blit(BACKGROUND, (0, 0))
        tela.blit(CLOUD, (0, 0))
        mensagem = f'Pontos: {chamine.pontos}'
        texto = fonte.render(mensagem, True, (255, 255, 255))
        ger = fonte.render(f'Geração: {geracao}', True, (255, 255, 255))
        eliminar = []
        tela.blit(texto, (largura-150, 5))
        tela.blit(ger, (0, 5))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()

        for i, noel in enumerate(jogador.noeis):
            lista_genomas[i].fitness += 0.1
            output = redes[i].activate(
                (noel[2], chamine.chamines[0][2], abs(noel[1] - chamine.chamines[0][1])))
            if output[0] > 0.7:
                noel[5] = True

        eliminar = jogador.colidir(chamine)

        if len(eliminar) > 0:
            for elimina in eliminar:
                lista_genomas[elimina].fitness -= 1
                lista_genomas.pop(elimina)
                redes.pop(elimina)

        if len(jogador.noeis) <= 0:
            break

        jogador.pula()
        jogador.update()

        chamine.movimentar()
        chamine.adicionarPresente()
        chamine.dificuldade()
        ponto = chamine.removerPresente()
        for i, genoma in enumerate(lista_genomas):
            lista_genomas[i].fitness += ponto
        pygame.display.flip()


def rodar(caminho_config):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                caminho_config)

    populacao = neat.Population(config)
    populacao.add_reporter(neat.StdOutReporter(True))
    populacao.add_reporter(neat.StatisticsReporter())

    populacao.run(main, 50)


if __name__ == "__main__":
    caminho = os.path.dirname(__file__)
    caminho_config = os.path.join(caminho, 'config.txt')
    rodar(caminho_config)
