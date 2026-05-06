from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db
from app.security.dependencies import RoleChecker

router = APIRouter()

# ADMIN: View all Users
@router.get("/employees", response_model=List[schemas.EmployeeResponse])
def get_all_employees(
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(RoleChecker({"Admin"})),
):
    employees = db.query(models.Employee).filter(models.Employee.is_active == True).all()  # noqa: E712
    return employees

@router.get("/customers", response_model=List[schemas.CustomerResponse])
def get_all_customers(
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(RoleChecker({"Admin"})),
):
    customers = db.query(models.Customer).filter(models.Customer.is_active == True).all() # noqa: E712
    return customers


# ADMIN: View all Soft Deleted Employees
@router.get("/employees/soft_deleted", response_model=List[schemas.EmployeeResponse])
def get_all_soft_deleted_employees(
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(RoleChecker({"Admin"})),
):
    users = db.query(models.Employee).filter(models.Employee.is_active == False).all()  # noqa: E712
    return users

# ADMIN: View all Soft Deleted Customers
@router.get("/customers/soft_deleted", response_model=List[schemas.CustomerResponse])
def get_all_soft_deleted_customers(
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(RoleChecker({"Admin"})),
):
    customers = db.query(models.Customer).filter(models.Customer.is_active == False).all()  # noqa: E712
    return customers

# ADMIN: Updates the User Roles
@router.put("/employees/{user_id}/role")
def update_employee_role(
    user_id: int,
    new_role: str,
    db: Session = Depends(get_db),

    # Privilege is strictly locked to Admin, so that only they may promote / demote
    current_user: models.Employee = Depends(RoleChecker({"Admin"}))
):
    valid_roles = {"Admin", "Analyst", "Viewer"}
    if new_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Role! Must be one of {valid_roles}",
        )
    
    user_query = db.query(models.Employee).filter(models.Employee.id == user_id)
    user = user_query.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user_query.update({"role": new_role}, synchronize_session=False)
    db.commit()

    return {"message": f"User: {user.username} role updated to {new_role}"}

# ADMIN: Soft Delete Users (Deactivation)
@router.delete("/employees/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_employee(
    user_id: int,
    db: Session = Depends(get_db),
    current_users: models.Employee = Depends(RoleChecker({"Admin"}))
):
    user_query = db.query(models.Employee).filter(models.Employee.id == user_id)
    user = user_query.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not Found"
        )
    
    # The Soft Delete: We don't delete the row, we just turn off the access
    user_query.update({"is_active": False}, synchronize_session=False)
    db.commit()

    return None

@router.delete("/customers/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_customer(
    user_id: int,
    db: Session = Depends(get_db),
    current_users: models.Employee = Depends(RoleChecker({"Admin"}))
):
    user_query = db.query(models.Customer).filter(models.Customer.id == user_id)
    user = user_query.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not Found"
        )
    
    # The Soft Delete: We don't delete the row, we just turn off the access
    user_query.update({"is_active": False}, synchronize_session=False)
    db.commit()

    return None