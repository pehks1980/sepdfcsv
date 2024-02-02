package main

import (
	"context"
	"flag"
	"log"
	"net"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/pehks1980/cache-serv/internal/app/endpoint"
	// сервис сервера ()
	"github.com/pehks1980/cache-serv/internal/app/service"
	// репозиторий (хранилище) 1 файло 2 память 3 pg sql(db)
	"github.com/pehks1980/cache-serv/internal/pkg/repository"

)


// главная петля
func main() {

	log.Print("Starting the cache-serv")
	// настройка порта, настроек хранилища, таймаут при закрытии сервиса
	port := flag.String("port", "8000", "Port")
	//storageName := flag.String("storage", "storage.json", "data storage")
	shutdownTimeout := flag.Int64("shutdown_timeout", 3, "shutdown timeout")
	// инициализация файлового хранилища ук на структуру repo
	var repoif repository.RepoIf
	// подстановка в интерфейс соотвествующего хранилища
	//repoif = new(repository.FileRepo)
	repoif = new(repository.MemRepo)
	//repoif = new(repository.PgRepo)
	
	// вызов доп метода интерфейса - инициализация
	config := `{"defexpiry": "10"}`

	repoif = repoif.New(config)

	// инициализация сервиса - 'сцепление' с файловым хранилищем
	queueSVC := service.New(repoif)
	//создание сервера с таким портом, и обработчиком интерфейс которого связывается а файлохранилищем
	ctx, cancel := context.WithCancel(context.Background())
	
	//
	queueSVC.Vacuum(ctx)

	serv := http.Server{
		Addr:    net.JoinHostPort("", *port),
		Handler: endpoint.RegisterPublicHTTP(queueSVC),
	}
	// запуск сервера
	go func() {
		if err := serv.ListenAndServe(); err != nil {
			log.Fatalf("listen and serve err: %v", err)
		}
	}()

	interrupt := make(chan os.Signal, 1)
	signal.Notify(interrupt, syscall.SIGINT, syscall.SIGTERM, os.Interrupt)

	log.Printf("Started app at :%s",*port)
	// ждет сигнала
	//time.Sleep(time.Duration(1) * time.Second)
	//cancel()

	sig := <-interrupt
	//stop vacuum
	cancel()

	ctx, cancel = context.WithTimeout(context.Background(), time.Duration(*shutdownTimeout)*time.Second)

	log.Printf("Sig: %v, stopping app", sig)
	// шат даун по контексту с тайм аутом
	
	
	defer cancel()
	if err := serv.Shutdown(ctx); err != nil {
		log.Printf("shutdown err: %v", err)
	}
}
