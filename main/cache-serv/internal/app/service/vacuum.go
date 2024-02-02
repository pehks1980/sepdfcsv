package service

import (
	"context"
	//"log"

	_ "github.com/pehks1980/cache-serv/internal/pkg/model"
	//cache_serv "github.com/pehks1980/cache-serv/pkg/cache-serv"
)

func (s *Service) Vacuum(ctx context.Context) {
	go s.repo.Vacuum(ctx)
}