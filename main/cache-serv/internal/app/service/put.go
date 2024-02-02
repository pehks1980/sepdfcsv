package service

import (
	"log"

	"github.com/pehks1980/cache-serv/internal/pkg/model"

	//cache_serv "github.com/pehks1980/cache-serv/pkg/cache-serv"
)

func (s *Service) Put(req *model.PutValue) error {
	if err := s.repo.Put(req); err != nil {
		log.Printf("service/Put: put repo err: %v", err)
		return err
	}

	return nil
}
