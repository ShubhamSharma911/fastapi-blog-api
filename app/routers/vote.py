from typing import List

from fastapi import FastAPI, HTTPException,APIRouter, Response, status,Depends
from sqlalchemy.orm import Session

from .. import schemas, database, models, oauth2

router = APIRouter(
    prefix="/vote",
    tags=["vote"]
)

@router.post("/", status_code=201)
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db), current_user: models.User = Depends(oauth2.get_current_user) ):

    post = db.query(models.Post).filter_by(id=vote.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post does not exist")

    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()
    if vote.dir == 1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= "user already voted on this post")
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        db.refresh(new_vote)
        return {"message": "successfully voted on this post"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "user already voted on this post")
        vote_query.delete(synchronize_session=False)
        db.commit()
        return{"message": "successfully deleted vote"}
